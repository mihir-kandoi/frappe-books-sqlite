"""Books-compatible transaction number series backed by Frappe records."""

import re

import frappe
from frappe import _

INVALID_PREFIX = re.compile(r"[/=?&%]")


class SeriesNamingMixin:
	def autoname(self):
		prefix = self.get("number_series")
		if prefix:
			self.name = next_name(prefix)


def next_name(prefix):
	series_doc = frappe.get_doc("Books Number Series", prefix)
	series = frappe.qb.DocType("Books Number Series")
	(frappe.qb.update(series).set(series.current, series.current + 1).where(series.name == prefix)).run()
	current = frappe.db.get_value("Books Number Series", prefix, "current")
	return f"{prefix}{int(current):0{series_doc.pad_zeros}d}"


def validate_series(series_doc):
	if INVALID_PREFIX.search(series_doc.name or ""):
		frappe.throw(_("Number-series prefixes cannot contain /, ?, &, =, or %."))
	if series_doc.start < 0:
		frappe.throw(_("Number-series start must be zero or greater."))
	if series_doc.pad_zeros < 0:
		frappe.throw(_("Number-series padding must be zero or greater."))
	if series_doc.is_new() and not series_doc.current:
		series_doc.current = series_doc.start - 1
