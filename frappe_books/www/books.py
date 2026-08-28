"""Boot context for the standalone Frappe Books Vue application."""

import json
import re

import frappe
import frappe.sessions
from frappe.utils.jinja_globals import is_rtl

no_cache = 1
SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>", re.IGNORECASE)
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>", re.IGNORECASE)


def get_context(context):
	context.no_cache = 1
	context.boot = _get_boot()
	context.app_name = (
		frappe.get_website_settings("app_name") or frappe.get_system_settings("app_name") or "Frappe"
	)
	context.layout_direction = "rtl" if is_rtl() else "ltr"
	context.lang = frappe.local.lang
	context.books_boot = json.dumps(_books_boot())
	return context


def _get_boot():
	try:
		boot = frappe.sessions.get()
	except Exception as exc:
		raise frappe.SessionBootFailed from exc
	boot_json = frappe.as_json(boot, indent=None, separators=(",", ":"))
	boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)
	boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)
	return json.dumps(boot_json)


def _books_boot():
	settings = frappe.get_single("Books Accounting Settings")
	country = settings.country or ""
	return {
		"country_code": {"India": "in", "Switzerland": "ch"}.get(country, "-"),
		"setup_complete": bool(settings.setup_complete),
		"app_version": frappe.get_attr("frappe_books.__version__"),
		"developer_mode": bool(frappe.conf.developer_mode),
	}
