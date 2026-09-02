"""Load and combine the JSON schemas used by the Books web interface."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

Schema = dict[str, Any]

APP_CORE_SCHEMAS = ("CustomField.json", "CustomForm.json", "SystemSettings.json")
HOSTED_PORT_FIELDS = {
	"SalesInvoiceItem": [
		{
			"fieldname": "serialNumber",
			"label": "Serial Number",
			"fieldtype": "Text",
			"section": "Inventory",
		}
	],
	"PurchaseInvoiceItem": [
		{
			"fieldname": "serialNumber",
			"label": "Serial Number",
			"fieldtype": "Text",
			"section": "Inventory",
		}
	],
}


def load_schemas(source_root: str | Path) -> dict[str, Schema]:
	"""Return concrete Books schemas with abstract and regional fields merged."""
	source_root = Path(source_root).resolve()
	paths = sorted((source_root / "schemas" / "app").rglob("*.json"))
	paths.extend(source_root / "schemas" / "core" / name for name in APP_CORE_SCHEMAS)

	raw_schemas: dict[str, Schema] = {}
	for path in paths:
		schema = json.loads(path.read_text())
		name = schema["name"]
		if name in raw_schemas:
			raise ValueError(f"Duplicate Books schema: {name}")
		raw_schemas[name] = schema

	abstract_names = {name for name, schema in raw_schemas.items() if schema.get("isAbstract")}
	concrete: dict[str, Schema] = {}
	for name, schema in raw_schemas.items():
		if name in abstract_names:
			continue

		base_name = schema.get("extends")
		if base_name in abstract_names:
			schema = _combine(schema, raw_schemas[base_name])
		else:
			schema = deepcopy(schema)

		_remove_fields(schema)
		schema.pop("extends", None)
		schema.pop("isAbstract", None)
		concrete[name] = schema

	_merge_regional_fields(source_root, concrete)
	_merge_hosted_port_fields(concrete)
	return concrete


def _merge_regional_fields(source_root: Path, schemas: dict[str, Schema]) -> None:
	"""Keep country-specific data portable by exposing all regional fields.

	The interface changes its schema at runtime based on the selected country.
	A Frappe site needs a stable database schema, so regional fields remain
	available and controllers decide when they apply.
	"""
	for path in sorted((source_root / "schemas" / "regional").glob("*/*.json")):
		regional = json.loads(path.read_text())
		base = schemas.get(regional["name"])
		if not base:
			continue
		known = {field["fieldname"] for field in base.get("fields", [])}
		for field in regional.get("fields", []):
			if field["fieldname"] not in known:
				base.setdefault("fields", []).append(deepcopy(field))
				known.add(field["fieldname"])


def _merge_hosted_port_fields(schemas: dict[str, Schema]) -> None:
	"""Add fields required by server workflows."""
	for schema_name, fields in HOSTED_PORT_FIELDS.items():
		schema = schemas.get(schema_name)
		if not schema:
			continue
		known = {field["fieldname"] for field in schema.get("fields", [])}
		for field in fields:
			if field["fieldname"] not in known:
				schema.setdefault("fields", []).append(deepcopy(field))


def _combine(extending: Schema, abstract: Schema) -> Schema:
	"""Match Books' base-first field merge, with subclass fields replacing by name."""
	combined = deepcopy(abstract)
	combined.update(deepcopy(extending))

	fields = {field["fieldname"]: deepcopy(field) for field in abstract.get("fields", [])}
	for field in extending.get("fields", []):
		fields[field["fieldname"]] = deepcopy(field)
	combined["fields"] = list(fields.values())
	return combined


def _remove_fields(schema: Schema) -> None:
	removed = set(schema.pop("removeFields", []))
	if not removed:
		return

	schema["fields"] = [field for field in schema.get("fields", []) if field["fieldname"] not in removed]
	for key in ("tableFields", "quickEditFields", "keywordFields"):
		schema[key] = [fieldname for fieldname in schema.get(key, []) if fieldname not in removed]
	if schema.get("linkDisplayField") in removed:
		schema.pop("linkDisplayField", None)
