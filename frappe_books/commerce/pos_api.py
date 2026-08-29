"""Whitelisted services used by the hosted Books point-of-sale page."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.utils import now_datetime

from frappe_books.accounting.money import as_decimal, rounded
from frappe_books.inventory.stock import stock_quantity


@frappe.whitelist()
def get_pos_context(search: str = "", limit: int = 80) -> dict[str, Any]:
	"""Return POS configuration, sellable items, parties, and payment methods."""
	_require_permission()
	settings = frappe.get_single("Books Pos Settings")
	profile = _profile(settings)
	location = _inventory_location(settings, profile)
	can_change_rate = bool(_profile_setting(profile, settings, "can_change_rate"))
	hide_unavailable = bool(_profile_setting(profile, settings, "hide_unavailable_items"))

	filters = {"item_usage": ["in", ["Sales", "Both"]]}
	or_filters = None
	if search:
		pattern = f"%{search}%"
		or_filters = {"name": ["like", pattern], "item_code": ["like", pattern], "barcode": search}
	items = frappe.get_all(
		"Books Item",
		filters=filters,
		or_filters=or_filters,
		fields=[
			"name",
			"item_code",
			"description",
			"image",
			"rate",
			"unit",
			"track_item",
			"has_batch",
			"has_serial_number",
		],
		order_by="name asc",
		limit=min(max(int(limit), 1), 200),
	)
	for item in items:
		item["available_quantity"] = float(stock_quantity(item.name, location)) if item.track_item else None
	if hide_unavailable:
		items = [item for item in items if not item.track_item or item.available_quantity > 0]

	return {
		"configured": bool(settings.default_account and settings.cash_account),
		"is_shift_open": bool(settings.is_shift_open),
		"location": location,
		"can_change_rate": can_change_rate,
		"items": items,
		"customers": frappe.get_all(
			"Books Party",
			filters={"role": ["in", ["Customer", "Both"]]},
			fields=["name", "phone"],
			order_by="name asc",
			limit=500,
		),
		"default_customer": (profile.pos_customer if profile else None)
		or frappe.db.get_single_value("Books Defaults", "pos_customer"),
		"payment_methods": frappe.get_all(
			"Books Payment Method", fields=["name", "type", "account"], order_by="name asc"
		),
	}


@frappe.whitelist(methods=["POST"])
def checkout(
	cart: list[dict[str, Any]],
	customer: str,
	payments: list[dict[str, Any]],
	coupon_codes: list[str] | None = None,
	redeem_loyalty_points: int = 0,
) -> dict[str, Any]:
	"""Submit one POS invoice and its split payments as a single transaction."""
	_require_permission()
	settings = frappe.get_single("Books Pos Settings")
	if not settings.is_shift_open:
		frappe.throw(_("Open a POS shift before checking out."))
	if not customer or not frappe.db.exists("Books Party", customer):
		frappe.throw(_("Select a valid customer."))
	if not cart:
		frappe.throw(_("Add at least one item to the cart."))

	profile = _profile(settings)
	location = _inventory_location(settings, profile)
	can_change_rate = bool(_profile_setting(profile, settings, "can_change_rate"))
	invoice = frappe.get_doc(
		{
			"doctype": "Books Sales Invoice",
			"party": customer,
			"account": settings.default_account,
			"date": now_datetime(),
			"is_pos": 1,
			"make_auto_stock_transfer": int(
				bool(frappe.db.get_single_value("Books Accounting Settings", "enable_inventory"))
			),
			"redeem_loyalty_points": int(bool(redeem_loyalty_points)),
			"loyalty_points": max(int(redeem_loyalty_points or 0), 0),
			"coupons": [{"coupons": code} for code in (coupon_codes or []) if code],
			"items": [_cart_row(row, can_change_rate) for row in cart],
		}
	).insert()
	invoice.flags.stock_location = location
	invoice.submit()

	if len(payments) == 1 and not as_decimal(payments[0].get("amount")):
		payments[0]["amount"] = invoice.base_grand_total
	payment_total = rounded(sum((as_decimal(row.get("amount")) for row in payments), as_decimal(0)))
	if payment_total != rounded(invoice.base_grand_total):
		frappe.throw(
			_("Payment total {0} must equal invoice total {1}.").format(
				payment_total, rounded(invoice.base_grand_total)
			)
		)
	payment_names = []
	for row in payments:
		amount = rounded(row.get("amount"))
		if amount <= 0:
			continue
		method = frappe.get_doc("Books Payment Method", row.get("payment_method"))
		payment_account = method.account or ("Cash" if method.type == "Cash" else None)
		if not payment_account:
			frappe.throw(_("Set an account on payment method {0}.").format(method.name))
		payment = frappe.get_doc(
			{
				"doctype": "Books Payment",
				"party": customer,
				"date": invoice.date,
				"payment_type": "Receive",
				"payment_method": method.name,
				"account": invoice.account,
				"payment_account": payment_account,
				"amount": amount,
				"payment_references": [
					{
						"reference_type": invoice.doctype,
						"reference_name": invoice.name,
						"amount": amount,
					}
				],
			}
		).insert()
		payment.submit()
		payment_names.append(payment.name)

	return {
		"invoice": invoice.name,
		"payments": payment_names,
		"grand_total": invoice.grand_total,
		"outstanding_amount": frappe.db.get_value(invoice.doctype, invoice.name, "outstanding_amount"),
	}


def _cart_row(row: dict[str, Any], can_change_rate: bool) -> dict[str, Any]:
	item_name = row.get("item")
	item = frappe.db.get_value(
		"Books Item",
		item_name,
		["rate", "unit", "track_item", "has_batch", "has_serial_number"],
		as_dict=True,
	)
	if not item:
		frappe.throw(_("Item {0} does not exist.").format(item_name))
	quantity = as_decimal(row.get("quantity"))
	if quantity <= 0:
		frappe.throw(_("POS item quantities must be greater than zero."))
	rate = as_decimal(row.get("rate")) if can_change_rate else as_decimal(item.rate)
	return {
		"item": item_name,
		"quantity": quantity,
		"rate": rate,
		"unit": item.unit,
		"transfer_unit": item.unit,
		"transfer_quantity": quantity,
		"unit_conversion_factor": 1,
		"batch": row.get("batch"),
		"serial_number": row.get("serial_number"),
	}


def _profile(settings):
	if settings.pos_profile and frappe.db.exists("Books Pos Profile", settings.pos_profile):
		return frappe.get_doc("Books Pos Profile", settings.pos_profile)
	return None


def _inventory_location(settings, profile):
	return (profile.inventory if profile else None) or settings.inventory or "Stores"


def _profile_setting(profile, settings, fieldname: str):
	"""Use an explicit profile value, including false, before the singleton fallback."""
	if profile is not None:
		value = profile.get(fieldname)
		if value is not None:
			return value
	return settings.get(fieldname)


def _require_permission() -> None:
	if not frappe.has_permission("Books Sales Invoice", ptype="create"):
		raise frappe.PermissionError
