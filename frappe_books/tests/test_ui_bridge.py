"""Integration coverage for the original Vue UI's Frappe compatibility layer."""

from base64 import b64encode
from datetime import datetime, timedelta

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import now_datetime

from frappe_books.tests.accounting import make_account, make_item, make_party, unique_name
from frappe_books.ui_api import lifecycle_action
from frappe_books.ui_bridge.database import BooksDatabaseBridge


class IntegrationTestUiBridge(IntegrationTestCase):
	def setUp(self):
		self.bridge = BooksDatabaseBridge()

	def test_single_read_omits_unstored_frappe_defaults(self):
		frappe.db.sql("delete from tabSingles where doctype = %s", "Books Pos Settings")

		self.assertEqual(
			self.bridge.get("POSSettings", "POSSettings"),
			{"name": "POSSettings"},
		)

	def test_crud_uses_desktop_names_and_iso_datetimes(self):
		name = unique_name("Web UOM")
		inserted = self.bridge.insert("UOM", {"name": name, "isWhole": True})

		self.assertEqual(inserted["name"], name)
		self.assertEqual(inserted["isWhole"], 1)
		self.assertEqual(inserted["createdBy"], frappe.session.user)
		self.assertEqual(inserted["modifiedBy"], frappe.session.user)
		self.assertIn("T", inserted["created"])
		self.assertEqual(self.bridge.get("UOM", name)["createdBy"], frappe.session.user)

		rows = self.bridge.get_all(
			"UOM",
			{
				"fields": ["*"],
				"filters": {"isWhole": ["=", True]},
			},
		)
		row = next(row for row in rows if row["name"] == name)
		self.assertEqual(row["createdBy"], frappe.session.user)

		next_modified = datetime.fromisoformat(inserted["modified"]) + timedelta(seconds=1)
		expected_modified = datetime.fromisoformat(inserted["modified"])
		expected_modified = expected_modified.replace(
			microsecond=expected_modified.microsecond // 1000 * 1000
		)
		self.bridge.update(
			"UOM",
			{
				"name": name,
				"isWhole": False,
				"modified": next_modified.isoformat(),
				"__expectedModified": expected_modified.isoformat(),
			},
		)
		self.assertEqual(self.bridge.get("UOM", name)["isWhole"], 0)
		with self.assertRaises(frappe.TimestampMismatchError):
			self.bridge.update(
				"UOM",
				{
					"name": name,
					"isWhole": True,
					"__expectedModified": inserted["modified"],
				},
			)

		self.bridge.delete("UOM", name)
		self.assertFalse(self.bridge.exists("UOM", name))

	def test_system_settings_round_trip_only_persisted_values(self):
		self.bridge.update(
			"SystemSettings",
			{"dateFormat": "yyyy-MM-dd", "darkMode": True},
		)

		settings = self.bridge.get("SystemSettings", "SystemSettings")

		self.assertEqual(settings["dateFormat"], "yyyy-MM-dd")
		self.assertEqual(settings["darkMode"], "1")
		self.assertEqual(
			frappe.db.get_single_value("Books System Settings", "date_format"),
			"yyyy-MM-dd",
		)
		self.assertEqual(
			frappe.db.get_single_value("Books System Settings", "dark_mode"),
			1,
		)

	def test_secret_single_values_are_not_returned(self):
		settings = frappe.get_single("Books Erp Next Sync Settings")
		settings.auth_token = "bridge-secret"
		settings.save(ignore_permissions=True)

		self.assertNotIn(
			"authToken",
			self.bridge.get("ERPNextSyncSettings", "ERPNextSyncSettings"),
		)
		self.assertEqual(
			self.bridge.get_single_values({"parent": "ERPNextSyncSettings", "fieldname": "authToken"}),
			[],
		)

	def test_doctype_references_are_translated_by_field_type(self):
		name = unique_name("Bridge Quote")

		inserted = self.bridge.insert(
			"SalesQuote",
			{
				"name": name,
				"numberSeries": "SQUOT-",
				"referenceType": "Party",
				"entryCurrency": "Party",
			},
		)

		self.assertEqual(inserted["referenceType"], "Party")
		self.assertEqual(inserted["entryCurrency"], "Party")
		self.assertEqual(
			frappe.db.get_value(
				"Books Sales Quote",
				name,
				["reference_type", "entry_currency"],
			),
			("Books Party", "Party"),
		)

	def test_child_tables_round_trip_through_draft_writes(self):
		account = make_account("Bridge Tax Account", root_type="Liability", account_type="Tax")
		name = unique_name("Bridge Tax")

		inserted = self.bridge.insert(
			"Tax",
			{
				"name": name,
				"details": [{"account": account.name, "rate": 10}],
			},
		)
		self.assertEqual(inserted["details"][0]["account"], account.name)
		self.assertEqual(inserted["details"][0]["rate"], 10)
		persisted = frappe.get_doc("Books Tax", name)
		self.assertEqual(len(persisted.details), 1)
		self.assertEqual(persisted.details[0].parent, name)

		self.bridge.update(
			"Tax",
			{
				"name": name,
				"details": [{"account": account.name, "rate": 18}],
			},
		)
		updated = self.bridge.get("Tax", name)
		self.assertEqual(len(updated["details"]), 1)
		self.assertEqual(updated["details"][0]["rate"], 18)

	def test_item_list_request_returns_created_items(self):
		income = make_account("Bridge Item Income", root_type="Income", account_type="Income Account")
		expense = make_account("Bridge Item Expense", root_type="Expense", account_type="Expense Account")
		item = make_item(income.name, expense.name, rate=42)

		rows = self.bridge.get_all(
			"Item",
			{"fields": ["*"], "filters": {}, "orderBy": ["created"]},
		)
		listed = next(row for row in rows if row["name"] == item.name)

		self.assertEqual(listed["unit"], "Unit")
		self.assertEqual(listed["rate"], 42)

	def test_double_encoded_attach_images_are_normalized(self):
		receivable = make_account("Bridge Image Receivable", account_type="Receivable")
		party = make_party(receivable.name)
		image = "data:image/png;base64,aW1hZ2UtYnl0ZXM="
		double_encoded = f"data:image/png;base64,{b64encode(image.encode()).decode()}"
		frappe.db.set_value("Books Party", party.name, "image", double_encoded)

		self.assertEqual(self.bridge.get("Party", party.name, ["image"])["image"], image)

		self.bridge.update("Party", {"name": party.name, "image": double_encoded})
		self.assertEqual(frappe.db.get_value("Books Party", party.name, "image"), image)

	def test_child_list_returns_parent_metadata_for_linked_entries(self):
		receivable = make_account("Bridge Linked Receivable", account_type="Receivable")
		income = make_account("Bridge Linked Income", root_type="Income", account_type="Income Account")
		expense = make_account("Bridge Linked Expense", root_type="Expense", account_type="Expense Account")
		party = make_party(receivable.name)
		item = make_item(income.name, expense.name)
		invoice_name = unique_name("Bridge Linked Invoice")
		self.bridge.insert(
			"SalesInvoice",
			{
				"name": invoice_name,
				"numberSeries": "SINV-",
				"party": party.name,
				"account": receivable.name,
				"date": now_datetime().isoformat(),
				"entryCurrency": "Party",
				"exchangeRate": 1,
				"items": [
					{
						"item": item.name,
						"account": income.name,
						"rate": 100,
						"quantity": 1,
					}
				],
			},
		)

		rows = self.bridge.get_all(
			"SalesInvoiceItem",
			{
				"fields": ["name", "parent", "parentSchemaName"],
				"filters": {"item": item.name},
			},
		)

		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]["parent"], invoice_name)
		self.assertEqual(rows[0]["parentSchemaName"], "SalesInvoice")

	def test_submit_and_cancel_use_atomic_server_lifecycle(self):
		receivable = make_account("Bridge Receivable", account_type="Receivable")
		income = make_account("Bridge Income", root_type="Income", account_type="Income Account")
		expense = make_account("Bridge Expense", root_type="Expense", account_type="Expense Account")
		frappe.db.set_single_value("Books Accounting Settings", "discount_account", expense.name)
		party = make_party(receivable.name)
		item = make_item(income.name, expense.name)
		invoice_name = unique_name("Bridge Sales Invoice")
		self.bridge.insert(
			"SalesInvoice",
			{
				"name": invoice_name,
				"numberSeries": "SINV-",
				"party": party.name,
				"account": receivable.name,
				"date": now_datetime().isoformat(),
				"entryCurrency": "Party",
				"exchangeRate": 1,
				"items": [
					{
						"item": item.name,
						"account": income.name,
						"rate": 100,
						"quantity": 2,
						"itemDiscountPercent": 10,
					}
				],
			},
		)
		invoice = frappe.get_doc("Books Sales Invoice", invoice_name)
		self.assertEqual(len(invoice.items), 1)
		self.assertEqual(invoice.items[0].parent, invoice_name)
		self.assertEqual(invoice.entry_currency, "Party")

		with self.assertRaises(frappe.ValidationError):
			self.bridge.update(
				"SalesInvoice",
				{"name": invoice.name, "submitted": True},
			)

		submitted = lifecycle_action("submit", "SalesInvoice", invoice.name)
		self.assertTrue(submitted["submitted"])
		self.assertTrue(
			frappe.db.exists(
				"Books Ledger Entry",
				{"voucher_type": invoice.doctype, "voucher_no": invoice.name, "reverted": 0},
			)
		)

		cancelled = lifecycle_action("cancel", "SalesInvoice", invoice.name)
		self.assertTrue(cancelled["cancelled"])
		self.assertTrue(
			frappe.db.exists(
				"Books Ledger Entry",
				{"voucher_type": invoice.doctype, "voucher_no": invoice.name, "reverted": 1},
			)
		)
