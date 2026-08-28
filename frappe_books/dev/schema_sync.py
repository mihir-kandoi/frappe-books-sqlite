"""Synchronize all desktop Books schemas into standard Frappe DocTypes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import frappe

from frappe_books.dev.doctype_builder import (
	MODULE,
	build_doctype,
	clone_definition,
	doctype_name,
	fieldname,
)
from frappe_books.dev.schema_loader import load_schemas

SCALAR_PROPERTIES = (
	"module",
	"custom",
	"istable",
	"issingle",
	"is_submittable",
	"is_tree",
	"nsm_parent_field",
	"track_changes",
	"editable_grid",
	"allow_rename",
	"autoname",
	"search_fields",
)


def sync(source_root: str | None = None) -> dict[str, Any]:
	"""Create or update all concrete Books DocTypes and return a sync summary."""
	root = Path(source_root).resolve() if source_root else _default_source_root()
	schemas = load_schemas(root)
	definitions = {name: build_doctype(schema, schemas) for name, schema in sorted(schemas.items())}

	created = _create_skeletons(definitions)
	updated = []
	for definition in definitions.values():
		_apply_definition(definition)
		updated.append(definition["name"])

	mapping_path = _write_mapping(schemas)
	frappe.clear_cache()
	return {
		"source_root": str(root),
		"schema_count": len(schemas),
		"created": created,
		"updated": updated,
		"mapping_path": str(mapping_path),
	}


def _create_skeletons(definitions: dict[str, dict[str, Any]]) -> list[str]:
	created = []
	for definition in definitions.values():
		name = definition["name"]
		if frappe.db.exists("DocType", name):
			continue
		skeleton = _skeleton_definition(definition)
		frappe.get_doc(skeleton).insert(ignore_permissions=True)
		created.append(name)
	return created


def _skeleton_definition(definition: dict[str, Any]) -> dict[str, Any]:
	skeleton = {
		"doctype": "DocType",
		"name": definition["name"],
		"module": MODULE,
		"custom": 0,
		"istable": definition["istable"],
		"issingle": definition["issingle"],
		"is_submittable": definition["is_submittable"],
		"is_tree": definition["is_tree"],
		"permissions": definition["permissions"],
		"fields": [],
	}
	if definition["is_tree"]:
		skeleton["nsm_parent_field"] = definition["nsm_parent_field"]
		skeleton["fields"] = [
			field
			for field in definition["fields"]
			if field["fieldname"] in {"parent_books_account", "is_group", "lft", "rgt", "old_parent"}
		]
	return skeleton


def _apply_definition(definition: dict[str, Any]) -> None:
	doc = frappe.get_doc("DocType", definition["name"])
	for property_name in SCALAR_PROPERTIES:
		doc.set(property_name, definition.get(property_name))
	doc.set("fields", [])
	for field in clone_definition(definition)["fields"]:
		doc.append("fields", field)
	doc.set("permissions", [])
	for permission in definition["permissions"]:
		doc.append("permissions", permission)
	doc.save(ignore_permissions=True)


def _write_mapping(schemas: dict[str, dict[str, Any]]) -> Path:
	mapping: dict[str, Any] = {"version": 1, "doctypes": {}}
	for source_name, schema in sorted(schemas.items()):
		field_mapping = {
			field["fieldname"]: fieldname(source_name, field["fieldname"])
			for field in schema.get("fields", [])
			if not field.get("abstract") and field.get("fieldtype")
		}
		field_mapping["name"] = "name" if source_name != "Account" else "account_name"
		mapping["doctypes"][source_name] = {
			"doctype": doctype_name(source_name),
			"fields": field_mapping,
		}

	path = Path(frappe.get_app_path("frappe_books", "schema_mapping.json"))
	path.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n")
	return path


def _default_source_root() -> Path:
	return Path(frappe.get_app_path("frappe_books")).parents[1]
