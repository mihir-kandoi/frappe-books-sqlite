"""Integration coverage for dashboard and native print surfaces."""

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils.print_utils import get_print

from frappe_books.dashboard import get_dashboard_data
from frappe_books.printing import ensure_print_formats
from frappe_books.tests.accounting import make_account, make_invoice, make_item, make_party


class IntegrationTestUiServices(IntegrationTestCase):
	def setUp(self):
		self.receivable = make_account("UI Receivable", account_type="Receivable")
		self.income = make_account("UI Sales", root_type="Income", account_type="Income Account")
		self.expense = make_account("UI Expense", root_type="Expense", account_type="Expense Account")
		frappe.db.set_single_value("Books Accounting Settings", "discount_account", self.expense.name)
		self.party = make_party(self.receivable.name)
		self.item = make_item(self.income.name, self.expense.name)
		self.invoice = make_invoice(
			"Books Sales Invoice",
			self.party.name,
			self.receivable.name,
			self.item.name,
			self.income.name,
		)
		self.invoice.submit()

	def test_dashboard_includes_submitted_invoice(self):
		data = get_dashboard_data()
		self.assertGreaterEqual(data["summary"]["sales"], self.invoice.base_grand_total)
		self.assertTrue(any(row.name == self.invoice.name for row in data["unpaid_sales"]))

	def test_native_print_format_renders_invoice(self):
		ensure_print_formats()
		html = get_print(
			self.invoice.doctype,
			self.invoice.name,
			print_format="Frappe Books - Sales Invoice",
		)
		self.assertIn(self.invoice.name, html)
		self.assertIn(self.party.name, html)
		self.assertIn("Grand Total", html)
