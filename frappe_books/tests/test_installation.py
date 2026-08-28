"""Installation metadata regressions."""

import frappe
from frappe.tests import IntegrationTestCase

from frappe_books.setup import DEFAULT_PRINT_TEMPLATE_FIELDS, ensure_default_records

POST_INSTALL_LINK_FIELDS = {
	"Books Pos Settings": ("inventory", "cash_account", "write_off_account", "default_account"),
	"Books Defaults": tuple(DEFAULT_PRINT_TEMPLATE_FIELDS),
}


class IntegrationTestInstallation(IntegrationTestCase):
	def test_post_install_links_have_no_doctype_defaults(self):
		for doctype, fieldnames in POST_INSTALL_LINK_FIELDS.items():
			meta = frappe.get_meta(doctype)
			for fieldname in fieldnames:
				with self.subTest(doctype=doctype, fieldname=fieldname):
					self.assertFalse(meta.get_field(fieldname).default)

	def test_print_template_defaults_are_seeded_after_records(self):
		ensure_default_records()
		settings = frappe.get_single("Books Defaults")

		for fieldname, template_name in DEFAULT_PRINT_TEMPLATE_FIELDS.items():
			with self.subTest(fieldname=fieldname):
				self.assertEqual(settings.get(fieldname), template_name)
