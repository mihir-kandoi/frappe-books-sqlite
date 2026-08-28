"""Installation metadata regressions."""

from pathlib import Path

import frappe
from frappe.tests import IntegrationTestCase

import frappe_books
from frappe_books.hooks import app_icon_route, app_icon_title, app_icon_url
from frappe_books.setup import (
	BOOKS_DESKTOP_ICON_LABEL,
	DEFAULT_PRINT_TEMPLATE_FIELDS,
	ensure_default_records,
	ensure_desktop_icons,
)

POST_INSTALL_LINK_FIELDS = {
	"Books Pos Settings": ("inventory", "cash_account", "write_off_account", "default_account"),
	"Books Defaults": tuple(DEFAULT_PRINT_TEMPLATE_FIELDS),
}


class IntegrationTestInstallation(IntegrationTestCase):
	def test_apps_screen_uses_packaged_books_icon(self):
		apps_screen = frappe.get_hooks("add_to_apps_screen", app_name="frappe_books")
		self.assertEqual(
			apps_screen,
			[
				{
					"name": "frappe_books",
					"logo": app_icon_url,
					"title": app_icon_title,
					"route": app_icon_route,
				}
			],
		)
		self.assertEqual(frappe.get_hooks("app_logo_url", app_name="frappe_books"), [app_icon_url])
		self.assertTrue((Path(frappe_books.__file__).parent / "public" / "books-logo.png").is_file())

	def test_desktop_icons_are_canonical(self):
		ensure_desktop_icons()

		self.assertEqual(
			frappe.get_all(
				"Desktop Icon",
				filters={"app": "frappe_books", "icon_type": "App"},
				pluck="name",
			),
			[BOOKS_DESKTOP_ICON_LABEL],
		)
		standard_framework_icon = frappe.db.exists(
			"Desktop Icon",
			{"app": "frappe", "icon_type": "App", "standard": 1},
		)
		if standard_framework_icon:
			self.assertFalse(
				frappe.db.exists(
					"Desktop Icon",
					{"app": "frappe", "icon_type": "App", "standard": 0},
				)
			)

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
