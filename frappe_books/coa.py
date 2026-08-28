"""Chart-of-accounts creation for the native Frappe setup flow."""

import json
from pathlib import Path

import frappe

META_KEYS = {"accountType", "accountNumber", "rootType", "isGroup"}


def ensure_standard_coa():
	chart = json.loads(_coa_path().read_text())
	_create_children(chart, parent=None, root_type=None)


def ensure_bank_account(bank_name):
	if frappe.db.exists("Books Account", bank_name):
		return bank_name
	return _create_account(
		bank_name,
		parent="Bank Accounts",
		root_type="Asset",
		account_type="Bank",
		is_group=False,
	).name


def ensure_discount_account():
	if frappe.db.exists("Books Account", "Discounts"):
		return "Discounts"
	return _create_account(
		"Discounts",
		parent="Indirect Income",
		root_type="Income",
		account_type="Income Account",
		is_group=False,
	).name


def ensure_account(label, parent, root_type, account_type=None, is_group=False):
	"""Create a named account when missing and return its document."""
	return _create_account(label, parent, root_type, account_type, is_group)


def _create_children(children, parent, root_type):
	for label, node in children.items():
		if label in META_KEYS:
			continue
		if parent is None:
			root_type = node["rootType"]
		child_nodes = [key for key in node if key not in META_KEYS]
		is_group = bool(node.get("isGroup", child_nodes))
		_create_account(
			label,
			parent=parent,
			root_type=root_type,
			account_type=node.get("accountType"),
			is_group=is_group,
		)
		_create_children(node, parent=label, root_type=root_type)


def _create_account(label, parent, root_type, account_type, is_group):
	if frappe.db.exists("Books Account", label):
		return frappe.get_doc("Books Account", label)
	return frappe.get_doc(
		{
			"doctype": "Books Account",
			"account_name": label,
			"parent_books_account": parent,
			"root_type": root_type,
			"account_type": account_type,
			"is_group": is_group,
		}
	).insert(ignore_permissions=True)


def _coa_path():
	return Path(__file__).with_name("data") / "standard_coa.json"
