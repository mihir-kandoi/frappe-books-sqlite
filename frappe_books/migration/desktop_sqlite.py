"""Import a desktop Frappe Books SQLite database without reposting transactions."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import frappe
from frappe.model.naming import set_new_name
from frappe.utils.nestedset import rebuild_tree

from frappe_books.setup import normalize_ledger_dates

MAPPING_PATH = Path(__file__).resolve().parents[1] / "schema_mapping.json"
ALLOWED_SUFFIXES = {".db", ".sqlite", ".sqlite3"}
SYSTEM_USERS = {None, "", "__SYSTEM__"}
META_FIELDS = {
	"cancelled",
	"created",
	"createdBy",
	"idx",
	"modified",
	"modifiedBy",
	"parent",
	"parentFieldname",
	"parentSchemaName",
	"submitted",
}


@frappe.whitelist()
def preview_database(file_url: str) -> dict[str, Any]:
	"""Validate an uploaded desktop database and return importable row counts."""
	frappe.only_for("System Manager")
	path = _uploaded_file_path(file_url)
	with DesktopDatabase(path) as source:
		return source.preview()


@frappe.whitelist(methods=["POST"])
def import_database_file(file_url: str) -> dict[str, Any]:
	"""Import an uploaded database, skipping records already present on this site."""
	frappe.only_for("System Manager")
	return import_database(_uploaded_file_path(file_url))


def import_database(path: str | Path) -> dict[str, Any]:
	"""Import mapped desktop records while preserving names and document status.

	Controllers are deliberately bypassed. The desktop database already contains
	ledger and stock-ledger rows, so submitting imported transactions would post
	them a second time.
	"""
	path = Path(path).expanduser().resolve()
	_savepoint = "frappe_books_desktop_import"
	frappe.db.savepoint(_savepoint)
	try:
		with DesktopDatabase(path) as source:
			result = DesktopImporter(source).run()
	except Exception:
		frappe.db.rollback(save_point=_savepoint)
		raise
	return result


class DesktopDatabase:
	"""Read-only, validated view of one desktop Books SQLite file."""

	def __init__(self, path: str | Path):
		self.path = Path(path).resolve()
		self.connection: sqlite3.Connection | None = None
		self.tables: set[str] = set()

	def __enter__(self) -> DesktopDatabase:
		if not self.path.is_file():
			raise FileNotFoundError(self.path)
		if self.path.suffix.lower() not in ALLOWED_SUFFIXES and not self.path.name.endswith(".books.db"):
			raise ValueError("Select a .books.db, .db, .sqlite, or .sqlite3 file")

		uri = f"file:{self.path.as_posix()}?mode=ro"
		self.connection = sqlite3.connect(uri, uri=True)
		self.connection.row_factory = sqlite3.Row
		integrity = self.connection.execute("pragma integrity_check").fetchone()[0]
		if integrity != "ok":
			raise ValueError(f"SQLite integrity check failed: {integrity}")
		self.tables = {
			row[0]
			for row in self.connection.execute(
				"select name from sqlite_master where type = 'table' and name not like 'sqlite_%'"
			)
		}
		if "SingleValue" not in self.tables:
			raise ValueError("This is not a Frappe Books desktop database: SingleValue is missing")
		return self

	def __exit__(self, *_args: object) -> None:
		if self.connection:
			self.connection.close()
		self.connection = None

	def rows(self, table: str, *, where: Mapping[str, Any] | None = None) -> Iterator[dict[str, Any]]:
		if table not in self.tables:
			return
		connection = self._connection()
		query = f"select * from {_quote_identifier(table)}"
		values: list[Any] = []
		if where:
			columns = self.columns(table)
			usable = {key: value for key, value in where.items() if key in columns}
			if usable:
				query += " where " + " and ".join(f"{_quote_identifier(key)} = ?" for key in usable)
				values.extend(usable.values())
		if "idx" in self.columns(table):
			query += " order by idx, rowid"
		for row in connection.execute(query, values):
			yield dict(row)

	def columns(self, table: str) -> set[str]:
		if table not in self.tables:
			return set()
		return {
			row[1] for row in self._connection().execute(f"pragma table_info({_quote_identifier(table)})")
		}

	def count(self, table: str) -> int:
		if table not in self.tables:
			return 0
		return int(
			self._connection().execute(f"select count(*) from {_quote_identifier(table)}").fetchone()[0]
		)

	def preview(self) -> dict[str, Any]:
		mapping = _mapping()
		counts = {}
		for source_name in mapping:
			count = self.count(source_name)
			if count:
				counts[source_name] = count
		single_count = self.count("SingleValue")
		return {
			"database": self.path.name,
			"size": self.path.stat().st_size,
			"tables": len(self.tables),
			"mapped_tables": len(counts),
			"records": sum(counts.values()) + single_count,
			"single_values": single_count,
			"counts": counts,
		}

	def _connection(self) -> sqlite3.Connection:
		if not self.connection:
			raise RuntimeError("Desktop database is not open")
		return self.connection


class DesktopImporter:
	"""Map desktop schema names and camelCase fields into Frappe DocTypes."""

	def __init__(self, source: DesktopDatabase):
		self.source = source
		self.mapping = _mapping()
		self.source_by_doctype = {
			config["doctype"]: source_name for source_name, config in self.mapping.items()
		}
		self.inserted: dict[str, int] = {}
		self.skipped: dict[str, int] = {}
		self.single_values = 0

	def run(self) -> dict[str, Any]:
		for source_name in self._parent_tables():
			self._import_table(source_name)
		self._import_singles()

		if frappe.db.table_exists("Books Account") and frappe.db.count("Books Account"):
			rebuild_tree("Books Account")
		normalize_ledger_dates()
		return {
			"database": self.source.path.name,
			"inserted": self.inserted,
			"skipped": self.skipped,
			"single_values": self.single_values,
			"inserted_total": sum(self.inserted.values()),
			"skipped_total": sum(self.skipped.values()),
		}

	def _parent_tables(self) -> list[str]:
		available: list[str] = []
		for source_name, config in self.mapping.items():
			doctype = config["doctype"]
			meta = frappe.get_meta(doctype)
			if source_name in self.source.tables and not meta.istable and not meta.issingle:
				available.append(source_name)

		priority = {
			"Currency": 10,
			"Account": 20,
			"UOM": 30,
			"Location": 40,
			"Party": 50,
			"Address": 60,
			"Item": 70,
			"Tax": 80,
			"NumberSeries": 90,
			"AccountingLedgerEntry": 900,
			"StockLedgerEntry": 910,
		}
		return sorted(available, key=lambda name: (priority.get(name, 500), name))

	def _import_table(self, source_name: str) -> None:
		config = self.mapping[source_name]
		target_doctype = config["doctype"]
		for source_row in self.source.rows(source_name):
			values = self._mapped_values(source_name, source_row)
			values["doctype"] = target_doctype
			if frappe.get_meta(target_doctype).is_submittable:
				values["docstatus"] = _docstatus(source_row)

			for field in frappe.get_meta(target_doctype).get_table_fields():
				values[field.fieldname] = self._children(
					source_name,
					source_row,
					field.fieldname,
					field.options,
				)

			doc = frappe.get_doc(values)
			if not doc.name:
				set_new_name(doc)
			if frappe.db.exists(target_doctype, doc.name):
				self._increment(self.skipped, target_doctype)
				continue

			doc.db_insert()
			for child in doc.get_all_children():
				child.db_insert()
			self._increment(self.inserted, target_doctype)

	def _children(
		self,
		parent_source: str,
		parent_row: Mapping[str, Any],
		target_fieldname: str,
		child_doctype: str,
	) -> list[dict[str, Any]]:
		child_source = self.source_by_doctype.get(child_doctype)
		if not child_source or child_source not in self.source.tables:
			return []
		source_fieldname = self._source_fieldname(parent_source, target_fieldname)
		parent_name = parent_row.get("name")
		where = {"parent": parent_name}
		if "parentFieldname" in self.source.columns(child_source):
			where["parentFieldname"] = source_fieldname

		children = []
		for index, source_row in enumerate(self.source.rows(child_source, where=where), start=1):
			values = self._mapped_values(child_source, source_row)
			values["doctype"] = child_doctype
			values["idx"] = source_row.get("idx") or index
			children.append(values)
		return children

	def _mapped_values(self, source_name: str, source_row: Mapping[str, Any]) -> dict[str, Any]:
		config = self.mapping[source_name]
		target_doctype = config["doctype"]
		meta = frappe.get_meta(target_doctype)
		values: dict[str, Any] = {}
		for source_fieldname, target_fieldname in config["fields"].items():
			if source_fieldname not in source_row or source_fieldname in META_FIELDS:
				continue
			if target_fieldname == "name":
				values["name"] = source_row[source_fieldname]
				continue
			field = meta.get_field(target_fieldname)
			if not field or field.fieldtype in frappe.model.table_fields:
				continue
			values[target_fieldname] = self._convert_value(field, source_row[source_fieldname])

		values.update(_audit_values(source_row))
		return values

	def _convert_value(self, field: Any, value: Any) -> Any:
		if value is None:
			return None
		if field.fieldtype == "Date" and isinstance(value, str):
			return value[:10]
		if field.fieldtype == "JSON" and isinstance(value, str):
			try:
				return json.loads(value)
			except json.JSONDecodeError:
				return value
		if field.fieldtype == "Link" and field.options == "DocType" and value in self.mapping:
			return self.mapping[value]["doctype"]
		return value

	def _source_fieldname(self, source_name: str, target_fieldname: str) -> str:
		for source_fieldname, mapped_fieldname in self.mapping[source_name]["fields"].items():
			if mapped_fieldname == target_fieldname:
				return source_fieldname
		return target_fieldname

	def _import_singles(self) -> None:
		grouped: dict[str, dict[str, Any]] = {}
		for row in self.source.rows("SingleValue"):
			parent = row.get("parent")
			fieldname = row.get("fieldname")
			if parent in self.mapping and fieldname:
				grouped.setdefault(str(parent), {})[str(fieldname)] = row.get("value")

		for source_name, config in self.mapping.items():
			target_doctype = config["doctype"]
			meta = frappe.get_meta(target_doctype)
			if not meta.issingle:
				continue
			source_values = grouped.get(source_name, {})
			for source_fieldname, value in source_values.items():
				target_fieldname = config["fields"].get(source_fieldname)
				field = meta.get_field(target_fieldname) if target_fieldname else None
				if not field or field.fieldtype in frappe.model.table_fields:
					continue
				frappe.db.set_single_value(
					target_doctype,
					target_fieldname,
					self._convert_value(field, value),
					update_modified=False,
				)
				self.single_values += 1
			self._import_single_children(source_name, target_doctype)

	def _import_single_children(self, source_name: str, target_doctype: str) -> None:
		for field in frappe.get_meta(target_doctype).get_table_fields():
			children = self._children(source_name, {"name": source_name}, field.fieldname, field.options)
			for values in children:
				values.update(
					{
						"parent": target_doctype,
						"parenttype": target_doctype,
						"parentfield": field.fieldname,
					}
				)
				child = frappe.get_doc(values)
				if not child.name:
					set_new_name(child)
				if frappe.db.exists(field.options, child.name):
					self._increment(self.skipped, field.options)
					continue
				child.db_insert()
				self._increment(self.inserted, field.options)

	@staticmethod
	def _increment(counter: dict[str, int], doctype: str) -> None:
		counter[doctype] = counter.get(doctype, 0) + 1


def _mapping() -> dict[str, dict[str, Any]]:
	return json.loads(MAPPING_PATH.read_text())["doctypes"]


def _audit_values(row: Mapping[str, Any]) -> dict[str, Any]:
	owner = row.get("createdBy")
	modified_by = row.get("modifiedBy")
	return {
		"creation": row.get("created"),
		"modified": row.get("modified"),
		"owner": "Administrator" if owner in SYSTEM_USERS else owner,
		"modified_by": "Administrator" if modified_by in SYSTEM_USERS else modified_by,
	}


def _docstatus(row: Mapping[str, Any]) -> int:
	if row.get("cancelled"):
		return 2
	if row.get("submitted"):
		return 1
	return 0


def _uploaded_file_path(file_url: str) -> Path:
	if not file_url:
		frappe.throw("Upload a desktop Books database first")
	file_names = frappe.get_all("File", filters={"file_url": file_url}, pluck="name", limit=1)
	if not file_names:
		frappe.throw("The uploaded File record was not found")
	path = Path(frappe.get_doc("File", file_names[0]).get_full_path()).resolve()
	if not path.is_file():
		frappe.throw("The uploaded database file no longer exists")
	return path


def _quote_identifier(value: str) -> str:
	return '"' + value.replace('"', '""') + '"'
