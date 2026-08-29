"""Installation metadata regressions."""

from pathlib import Path

import frappe
from frappe.tests import IntegrationTestCase

import frappe_books
from frappe_books.boot import boot_session
from frappe_books.hooks import app_icon_route, app_icon_title, app_icon_url
from frappe_books.setup import (
	BOOKS_DESKTOP_ICON_INDEX,
	BOOKS_DESKTOP_ICON_LABEL,
	DEFAULT_PRINT_TEMPLATE_FIELDS,
	FRAMEWORK_DESKTOP_ICON_INDEX,
	after_app_install,
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
					"sequence_id": 10,
				}
			],
		)
		self.assertEqual(frappe.get_hooks("app_logo_url", app_name="frappe_books"), [app_icon_url])
		self.assertTrue((Path(frappe_books.__file__).parent / "public" / "books-icon.png").is_file())

	def test_boot_session_places_framework_before_installed_apps(self):
		self.assertEqual(
			frappe.get_hooks("boot_session", app_name="frappe_books"),
			["frappe_books.boot.boot_session"],
		)
		bootinfo = frappe._dict(
			app_data=[
				frappe._dict(app_name="frappe_books", sequence_id=10),
				frappe._dict(app_name="another_app", sequence_id=100),
				frappe._dict(app_name="frappe", sequence_id=1000),
			]
		)

		boot_session(bootinfo)

		self.assertEqual(
			[app.app_name for app in sorted(bootinfo.app_data, key=lambda app: app.sequence_id)],
			["frappe", "frappe_books", "another_app"],
		)

	def test_books_pages_use_packaged_icon(self):
		package_root = Path(frappe_books.__file__).parent
		for relative_path in ("www/books.html", "public/books/index.html"):
			with self.subTest(relative_path=relative_path):
				html = (package_root / relative_path).read_text()
				self.assertIn("/assets/frappe_books/books-icon.png", html)
				self.assertNotIn("/assets/frappe_books/books-logo.png", html)

	def test_desktop_icons_are_canonical(self):
		ensure_desktop_icons()

		self.assertEqual(
			frappe.get_all(
				"Desktop Icon",
				filters={"app": "frappe_books", "icon_type": "App"},
				fields=["name", "idx"],
			),
			[{"name": BOOKS_DESKTOP_ICON_LABEL, "idx": BOOKS_DESKTOP_ICON_INDEX}],
		)
		standard_framework_icon = frappe.db.exists(
			"Desktop Icon",
			{"app": "frappe", "icon_type": "App", "standard": 1},
		)
		if standard_framework_icon:
			self.assertEqual(
				frappe.db.get_value("Desktop Icon", standard_framework_icon, "idx"),
				FRAMEWORK_DESKTOP_ICON_INDEX,
			)
			self.assertFalse(
				frappe.db.exists(
					"Desktop Icon",
					{"app": "frappe", "icon_type": "App", "standard": 0},
				)
			)

	def test_post_install_repair_runs_after_frappe_icon_generation(self):
		self.assertEqual(
			frappe.get_hooks("after_app_install", app_name="frappe_books"),
			["frappe_books.setup.after_app_install"],
		)
		standard_framework_icon = frappe.db.exists(
			"Desktop Icon",
			{"app": "frappe", "icon_type": "App", "standard": 1},
		)
		if not standard_framework_icon:
			return

		frappe.get_doc(
			{
				"doctype": "Desktop Icon",
				"label": "Frappe Framework",
				"app": "frappe",
				"icon_type": "App",
				"idx": 0,
			}
		).insert(ignore_permissions=True)

		after_app_install("another_app")

		self.assertFalse(frappe.db.exists("Desktop Icon", "Frappe Framework"))
		self.assertEqual(
			frappe.db.get_value("Desktop Icon", standard_framework_icon, "idx"),
			FRAMEWORK_DESKTOP_ICON_INDEX,
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
