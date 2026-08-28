"""India GSTR-1 and GSTR-2 report rows."""

import frappe
from frappe import _

from frappe_books.accounting.money import as_decimal, rounded
from frappe_books.regional import INDIAN_STATES


def execute(gstr_type, filters=None):
	filters = frappe._dict(filters or {})
	doctype = "Books Sales Invoice" if gstr_type == "GSTR-1" else "Books Purchase Invoice"
	db_filters = {"docstatus": 1}
	if filters.from_date and filters.to_date:
		db_filters["date"] = ["between", [filters.from_date, filters.to_date]]
	elif filters.from_date:
		db_filters["date"] = [">=", filters.from_date]
	elif filters.to_date:
		db_filters["date"] = ["<=", filters.to_date]
	rows = []
	for name in frappe.get_all(doctype, filters=db_filters, order_by="date asc", pluck="name"):
		row = _invoice_row(frappe.get_doc(doctype, name))
		if _matches_filters(row, filters):
			rows.append(row)
	return _columns(), rows


def _invoice_row(invoice):
	party = frappe.get_doc("Books Party", invoice.party)
	company_gstin = frappe.db.get_single_value("Books Accounting Settings", "gstin") or ""
	place = ""
	if party.address:
		place = frappe.db.get_value("Books Address", party.address, "pos") or ""
	if not place and party.gstin:
		place = INDIAN_STATES.get(party.gstin[:2], "")
	in_state = bool(company_gstin and INDIAN_STATES.get(company_gstin[:2]) == place)
	tax_amounts = {"IGST": as_decimal(0), "CGST": as_decimal(0), "SGST": as_decimal(0)}
	total_rate = as_decimal(0)
	for tax in invoice.taxes:
		total_rate += as_decimal(tax.rate)
		if tax.account in tax_amounts:
			tax_amounts[tax.account] += as_decimal(tax.amount)
	taxable_value = sum((as_decimal(item.item_discounted_total) for item in invoice.items), as_decimal(0))
	if not invoice.discount_after_tax:
		taxable_value -= as_decimal(invoice.discount_amount)
	return {
		"gstin": party.gstin or "",
		"party_name": party.name,
		"invoice_no": invoice.name,
		"invoice_date": invoice.date,
		"invoice_value": rounded(invoice.grand_total),
		"place_of_supply": place,
		"reverse_charge": "N" if party.gstin else "Y",
		"rate": total_rate,
		"taxable_value": rounded(taxable_value),
		"integrated_tax": rounded(tax_amounts["IGST"]),
		"central_tax": rounded(tax_amounts["CGST"]),
		"state_tax": rounded(tax_amounts["SGST"]),
		"in_state": in_state,
	}


def _matches_filters(row, filters):
	if filters.place_of_supply and row["place_of_supply"] != filters.place_of_supply:
		return False
	transfer_type = filters.transfer_type
	if transfer_type == "B2B":
		return bool(row["gstin"])
	if transfer_type == "B2CL":
		return not row["gstin"] and not row["in_state"] and row["invoice_value"] >= 250000
	if transfer_type == "B2CS":
		return not row["gstin"] and (row["in_state"] or row["invoice_value"] < 250000)
	if transfer_type == "NR":
		return row["rate"] == 0
	return True


def _columns():
	return [
		{"label": _("GSTIN"), "fieldname": "gstin", "fieldtype": "Data", "width": 140},
		{
			"label": _("Party"),
			"fieldname": "party_name",
			"fieldtype": "Link",
			"options": "Books Party",
			"width": 180,
		},
		{"label": _("Invoice"), "fieldname": "invoice_no", "fieldtype": "Data", "width": 140},
		{"label": _("Invoice Date"), "fieldname": "invoice_date", "fieldtype": "Date", "width": 105},
		{"label": _("Invoice Value"), "fieldname": "invoice_value", "fieldtype": "Currency", "width": 120},
		{"label": _("Place of Supply"), "fieldname": "place_of_supply", "fieldtype": "Data", "width": 160},
		{"label": _("Reverse Charge"), "fieldname": "reverse_charge", "fieldtype": "Data", "width": 105},
		{"label": _("Rate"), "fieldname": "rate", "fieldtype": "Percent", "width": 80},
		{"label": _("Taxable Value"), "fieldname": "taxable_value", "fieldtype": "Currency", "width": 120},
		{"label": _("Integrated Tax"), "fieldname": "integrated_tax", "fieldtype": "Currency", "width": 110},
		{"label": _("Central Tax"), "fieldname": "central_tax", "fieldtype": "Currency", "width": 105},
		{"label": _("State Tax"), "fieldname": "state_tax", "fieldtype": "Currency", "width": 105},
	]
