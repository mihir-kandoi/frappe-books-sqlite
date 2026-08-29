"""Summary data for the hosted Books dashboard."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import add_months, get_first_day, get_last_day, getdate, today

from frappe_books.accounting.money import as_decimal, rounded
from frappe_books.reporting.financial import profit_and_loss


@frappe.whitelist()
def get_dashboard_data() -> dict[str, Any]:
	"""Return accounting KPIs, six-month trends, and unpaid invoices."""
	if not frappe.has_permission("Books Sales Invoice", ptype="read"):
		raise frappe.PermissionError
	settings = frappe.get_single("Books Accounting Settings")
	to_date = getdate(today())
	from_date = settings.fiscal_year_start or get_first_day(to_date.replace(month=1, day=1))
	_, profit_rows = profit_and_loss({"from_date": from_date, "to_date": to_date})
	profit = next(
		(as_decimal(row["amount"]) for row in profit_rows if row["account"] == "Net Profit / Loss"),
		as_decimal(0),
	)

	return {
		"company": settings.company_name or "Frappe Books",
		"period": {"from_date": from_date, "to_date": to_date},
		"summary": {
			"sales": _invoice_total("Books Sales Invoice", from_date, to_date),
			"purchases": _invoice_total("Books Purchase Invoice", from_date, to_date),
			"receivable": _outstanding_total("Books Sales Invoice"),
			"payable": _outstanding_total("Books Purchase Invoice"),
			"profit": rounded(profit),
		},
		"trend": _monthly_trend(to_date),
		"unpaid_sales": _unpaid("Books Sales Invoice"),
		"unpaid_purchases": _unpaid("Books Purchase Invoice"),
	}


def _invoice_total(doctype: str, from_date, to_date):
	values = frappe.get_all(
		doctype,
		filters={"docstatus": 1, "date": ["between", [from_date, to_date]]},
		pluck="base_grand_total",
	)
	return rounded(sum((as_decimal(value) for value in values), as_decimal(0)))


def _outstanding_total(doctype: str):
	values = frappe.get_all(
		doctype,
		filters={"docstatus": 1, "outstanding_amount": ["!=", 0]},
		pluck="outstanding_amount",
	)
	return rounded(sum((abs(as_decimal(value)) for value in values), as_decimal(0)))


def _monthly_trend(to_date) -> list[dict[str, Any]]:
	trend = []
	for offset in range(-5, 1):
		month = add_months(to_date, offset)
		start = get_first_day(month)
		end = get_last_day(month)
		trend.append(
			{
				"label": start.strftime("%b %Y"),
				"sales": _invoice_total("Books Sales Invoice", start, end),
				"purchases": _invoice_total("Books Purchase Invoice", start, end),
			}
		)
	return trend


def _unpaid(doctype: str) -> list[dict[str, Any]]:
	return frappe.get_all(
		doctype,
		filters={"docstatus": 1, "outstanding_amount": ["!=", 0]},
		fields=["name", "party", "date", "grand_total", "outstanding_amount"],
		order_by="date desc, creation desc",
		limit=8,
	)
