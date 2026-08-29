"""Unit coverage for generated Frappe DocType definitions."""

from frappe.tests import UnitTestCase

from frappe_books.dev.doctype_builder import build_naming


class TestDocTypeBuilder(UnitTestCase):
	def test_desktop_autoincrement_uses_sqlite_safe_numeric_format(self):
		self.assertEqual(
			build_naming({"name": "ItemEnquiry", "naming": "autoincrement"}),
			{"autoname": "format:{##########}"},
		)
