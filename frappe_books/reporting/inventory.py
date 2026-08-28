"""Stock ledger and stock balance report calculations."""

from collections import defaultdict, deque

import frappe
from frappe import _
from frappe.utils import get_datetime

from frappe_books.accounting.money import as_decimal, rounded


def stock_ledger(filters=None):
	filters = frappe._dict(filters or {})
	rows = _computed_entries(filters)
	return _ledger_columns(), rows


def stock_balance(filters=None):
	filters = frappe._dict(filters or {})
	rows = _computed_entries(filters, include_before=True)
	grouped = defaultdict(_empty_balance)
	from_date = get_datetime(filters.from_date) if filters.from_date else None
	to_date = get_datetime(filters.to_date) if filters.to_date else None
	for row in rows:
		key = (row["item"], row["location"], row.get("batch") or "")
		balance = grouped[key]
		balance.update({"item": row["item"], "location": row["location"], "batch": row.get("batch")})
		date = get_datetime(row["date"])
		quantity = as_decimal(row["quantity"])
		value = as_decimal(row["value_change"])
		if from_date and date < from_date:
			balance["opening_quantity"] += quantity
			balance["opening_value"] += value
		elif not to_date or date <= to_date:
			if quantity >= 0:
				balance["incoming_quantity"] += quantity
				balance["incoming_value"] += value
			else:
				balance["outgoing_quantity"] += abs(quantity)
				balance["outgoing_value"] += abs(value)
	data = []
	for balance in grouped.values():
		balance["balance_quantity"] = (
			balance["opening_quantity"] + balance["incoming_quantity"] - balance["outgoing_quantity"]
		)
		balance["balance_value"] = (
			balance["opening_value"] + balance["incoming_value"] - balance["outgoing_value"]
		)
		balance["valuation_rate"] = rounded(
			balance["balance_value"] / balance["balance_quantity"] if balance["balance_quantity"] else 0
		)
		data.append(
			{key: rounded(value) if hasattr(value, "quantize") else value for key, value in balance.items()}
		)
	data.sort(key=lambda row: (row["item"], row["location"], row.get("batch") or ""))
	return _balance_columns(), data


def _computed_entries(filters, include_before=False):
	db_filters = {}
	for fieldname in ("item", "location", "batch", "serial_number", "reference_type", "reference_name"):
		if filters.get(fieldname):
			db_filters[fieldname] = filters[fieldname]
	if not include_before:
		if filters.get("from_date") and filters.get("to_date"):
			db_filters["date"] = ["between", [filters.from_date, filters.to_date]]
		elif filters.get("from_date"):
			db_filters["date"] = [">=", filters.from_date]
		elif filters.get("to_date"):
			db_filters["date"] = ["<=", filters.to_date]
	elif filters.get("to_date"):
		db_filters["date"] = ["<=", filters.to_date]
	raw = frappe.get_all(
		"Books Stock Ledger Entry",
		filters=db_filters,
		fields=[
			"date",
			"item",
			"location",
			"batch",
			"serial_number",
			"quantity",
			"rate",
			"reference_type",
			"reference_name",
		],
		order_by="date asc, creation asc",
	)
	layers = defaultdict(deque)
	balances = defaultdict(lambda: {"quantity": as_decimal(0), "value": as_decimal(0)})
	computed = []
	for row in raw:
		key = (row.item, row.location, row.batch or "")
		quantity = as_decimal(row.quantity)
		rate = as_decimal(row.rate)
		value_change = as_decimal(0)
		if quantity > 0:
			layers[key].append([quantity, rate])
			value_change = quantity * rate
		elif quantity < 0:
			remaining = abs(quantity)
			while remaining and layers[key]:
				layer_quantity, layer_rate = layers[key][0]
				taken = min(remaining, layer_quantity)
				value_change -= taken * layer_rate
				remaining -= taken
				layer_quantity -= taken
				if layer_quantity:
					layers[key][0][0] = layer_quantity
				else:
					layers[key].popleft()
			if remaining:
				value_change -= remaining * rate
		balances[key]["quantity"] += quantity
		balances[key]["value"] += value_change
		balance_quantity = balances[key]["quantity"]
		balance_value = balances[key]["value"]
		valuation_rate = balance_value / balance_quantity if balance_quantity else as_decimal(0)
		computed.append(
			{
				**row,
				"incoming_rate": rounded(rate if quantity > 0 else 0),
				"value_change": rounded(value_change),
				"balance_quantity": balance_quantity,
				"balance_value": rounded(balance_value),
				"valuation_rate": rounded(valuation_rate),
			}
		)
	return computed


def _empty_balance():
	return {
		"opening_quantity": as_decimal(0),
		"opening_value": as_decimal(0),
		"incoming_quantity": as_decimal(0),
		"incoming_value": as_decimal(0),
		"outgoing_quantity": as_decimal(0),
		"outgoing_value": as_decimal(0),
	}


def _ledger_columns():
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Datetime", "width": 150},
		{"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Books Item", "width": 180},
		{
			"label": _("Location"),
			"fieldname": "location",
			"fieldtype": "Link",
			"options": "Books Location",
			"width": 130,
		},
		{
			"label": _("Batch"),
			"fieldname": "batch",
			"fieldtype": "Link",
			"options": "Books Batch",
			"width": 120,
		},
		{
			"label": _("Serial Number"),
			"fieldname": "serial_number",
			"fieldtype": "Link",
			"options": "Books Serial Number",
			"width": 140,
		},
		{"label": _("Quantity"), "fieldname": "quantity", "fieldtype": "Float", "width": 100},
		{"label": _("Balance Qty"), "fieldname": "balance_quantity", "fieldtype": "Float", "width": 110},
		{"label": _("Incoming Rate"), "fieldname": "incoming_rate", "fieldtype": "Currency", "width": 120},
		{"label": _("Valuation Rate"), "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 120},
		{"label": _("Balance Value"), "fieldname": "balance_value", "fieldtype": "Currency", "width": 120},
		{"label": _("Value Change"), "fieldname": "value_change", "fieldtype": "Currency", "width": 120},
		{
			"label": _("Reference Type"),
			"fieldname": "reference_type",
			"fieldtype": "Link",
			"options": "DocType",
			"width": 170,
		},
		{
			"label": _("Reference"),
			"fieldname": "reference_name",
			"fieldtype": "Dynamic Link",
			"options": "reference_type",
			"width": 160,
		},
	]


def _balance_columns():
	return [
		{"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Books Item", "width": 180},
		{
			"label": _("Location"),
			"fieldname": "location",
			"fieldtype": "Link",
			"options": "Books Location",
			"width": 130,
		},
		{
			"label": _("Batch"),
			"fieldname": "batch",
			"fieldtype": "Link",
			"options": "Books Batch",
			"width": 120,
		},
		{"label": _("Opening Qty"), "fieldname": "opening_quantity", "fieldtype": "Float", "width": 105},
		{"label": _("Opening Value"), "fieldname": "opening_value", "fieldtype": "Currency", "width": 115},
		{"label": _("In Qty"), "fieldname": "incoming_quantity", "fieldtype": "Float", "width": 90},
		{"label": _("In Value"), "fieldname": "incoming_value", "fieldtype": "Currency", "width": 110},
		{"label": _("Out Qty"), "fieldname": "outgoing_quantity", "fieldtype": "Float", "width": 90},
		{"label": _("Out Value"), "fieldname": "outgoing_value", "fieldtype": "Currency", "width": 110},
		{"label": _("Balance Qty"), "fieldname": "balance_quantity", "fieldtype": "Float", "width": 105},
		{"label": _("Balance Value"), "fieldname": "balance_value", "fieldtype": "Currency", "width": 115},
		{"label": _("Valuation Rate"), "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 115},
	]
