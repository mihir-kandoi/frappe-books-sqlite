"""Translate desktop Books schema names and fields to hosted DocTypes."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import frappe

MAPPING_PATH = Path(__file__).resolve().parents[1] / "schema_mapping.json"
SOURCE_META_TO_TARGET = {
	"name": "name",
	"created": "creation",
	"createdBy": "owner",
	"modified": "modified",
	"modifiedBy": "modified_by",
	"idx": "idx",
	"parent": "parent",
	"parentFieldname": "parentfield",
	"parentSchemaName": "parenttype",
}


@lru_cache(maxsize=1)
def schema_mapping() -> dict[str, dict[str, Any]]:
	return json.loads(MAPPING_PATH.read_text())["doctypes"]


@lru_cache(maxsize=1)
def source_by_doctype() -> dict[str, str]:
	return {config["doctype"]: source for source, config in schema_mapping().items()}


def target_doctype(source_schema: str) -> str:
	if not isinstance(source_schema, str):
		frappe.throw("Books schema names must be strings")
	config = schema_mapping().get(source_schema)
	if not config:
		frappe.throw(f"Unsupported Books schema: {source_schema}")
	return config["doctype"]


def target_field(source_schema: str, source_field: str) -> str:
	if not isinstance(source_field, str):
		frappe.throw("Books field names must be strings")
	if source_field in SOURCE_META_TO_TARGET:
		return SOURCE_META_TO_TARGET[source_field]
	if source_field in {"submitted", "cancelled"}:
		return "docstatus"
	fields = schema_mapping()[source_schema]["fields"]
	if source_field not in fields:
		frappe.throw(f"Unsupported field {source_field} for Books schema {source_schema}")
	return fields[source_field]


def source_field(source_schema: str, target_fieldname: str) -> str:
	for source_name, target_name in SOURCE_META_TO_TARGET.items():
		if target_name == target_fieldname:
			return source_name
	for source_name, target_name in schema_mapping()[source_schema]["fields"].items():
		if target_name == target_fieldname:
			return source_name
	return target_fieldname


def target_reference(value: Any) -> Any:
	if isinstance(value, str) and value in schema_mapping():
		return schema_mapping()[value]["doctype"]
	return value


def source_reference(value: Any) -> Any:
	if isinstance(value, str):
		return source_by_doctype().get(value, value)
	return value
