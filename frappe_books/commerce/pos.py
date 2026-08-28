"""Point-of-sale shift opening, reconciliation, and cash posting."""

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import now_datetime

from frappe_books.accounting.money import as_decimal, rounded


def prepare_opening_shift(shift):
	if not shift.opening_date:
		shift.opening_date = now_datetime()
	_validate_cash_rows(shift.opening_cash)
	amounts = _amount_map(shift.opening_amounts, "amount")
	cash_total = _cash_total(shift.opening_cash)
	if rounded(amounts.get("Cash", 0)) != cash_total:
		frappe.throw(_("Opening Cash amount must equal the denomination total."))
	if _open_shift_name():
		frappe.throw(_("A POS shift is already open."))


def activate_opening_shift(shift):
	_set_shift_open(True)
	cash_total = _cash_total(shift.opening_cash)
	if cash_total:
		settings = frappe.get_single("Books Pos Settings")
		_make_cash_journal(
			shift.opening_date,
			[(settings.cash_account, cash_total, 0), (_cash_account(), 0, cash_total)],
			_("POS opening shift {0}").format(shift.name),
		)


def prevent_open_shift_delete(shift):
	if not frappe.db.exists("Books Pos Closing Shift", {"opening_shift": shift.name}):
		frappe.throw(_("Close the POS shift before deleting it."))


def prepare_closing_shift(shift):
	if not shift.opening_shift:
		shift.opening_shift = _open_shift_name()
	if not shift.opening_shift:
		frappe.throw(_("There is no open POS shift to close."))
	if frappe.db.exists("Books Pos Closing Shift", {"opening_shift": shift.opening_shift}):
		frappe.throw(_("POS shift {0} has already been closed.").format(shift.opening_shift))
	if not shift.closing_date:
		shift.closing_date = now_datetime()
	_validate_cash_rows(shift.closing_cash)
	_seed_expected_amounts(shift)
	for row in shift.closing_amounts:
		if as_decimal(row.closing_amount) < 0:
			frappe.throw(_("Closing amounts cannot be negative."))
		row.difference_amount = rounded(as_decimal(row.closing_amount) - as_decimal(row.expected_amount))
	cash_total = _cash_total(shift.closing_cash)
	cash_row = next((row for row in shift.closing_amounts if row.payment_method == "Cash"), None)
	if cash_row and cash_total != rounded(cash_row.closing_amount):
		frappe.throw(_("Closing Cash amount must equal the denomination total."))


def close_shift(shift):
	_set_shift_open(False)
	cash_row = next((row for row in shift.closing_amounts if row.payment_method == "Cash"), None)
	if not cash_row or not as_decimal(cash_row.expected_amount):
		return
	settings = frappe.get_single("Books Pos Settings")
	closing = rounded(cash_row.closing_amount)
	difference = rounded(cash_row.difference_amount)
	rows = [(_cash_account(), closing, 0), (settings.cash_account, 0, closing)]
	if difference < 0:
		rows.extend([(_cash_account(), abs(difference), 0), (settings.write_off_account, 0, abs(difference))])
	elif difference > 0:
		rows.extend([(settings.write_off_account, difference, 0), (_cash_account(), 0, difference)])
	_make_cash_journal(
		shift.closing_date,
		rows,
		_("POS closing shift {0}").format(shift.name),
	)


def transacted_amounts(from_date, to_date):
	invoice_names = frappe.get_all(
		"Books Sales Invoice",
		filters={"is_pos": 1, "docstatus": 1, "date": ["between", [from_date, to_date]]},
		pluck="name",
	)
	if not invoice_names:
		return {}
	payments = frappe.get_all(
		"Books Payment For",
		filters={"reference_type": "Books Sales Invoice", "reference_name": ["in", invoice_names]},
		fields=["parent", "reference_name"],
	)
	result = defaultdict(as_decimal)
	for reference in payments:
		payment = frappe.db.get_value(
			"Books Payment",
			{"name": reference.parent, "docstatus": 1},
			["payment_method", "amount"],
			as_dict=True,
		)
		if not payment:
			continue
		sign = (
			-1
			if frappe.db.get_value("Books Sales Invoice", reference.reference_name, "return_against")
			else 1
		)
		result[payment.payment_method] += sign * as_decimal(payment.amount)
	return {method: rounded(amount) for method, amount in result.items()}


def _seed_expected_amounts(shift):
	opening = frappe.get_doc("Books Pos Opening Shift", shift.opening_shift)
	transactions = transacted_amounts(opening.opening_date, shift.closing_date)
	existing = {row.payment_method: row for row in shift.closing_amounts}
	shift.set("closing_amounts", [])
	for row in opening.opening_amounts:
		closing = existing.get(row.payment_method)
		opening_amount = rounded(row.amount)
		expected = rounded(opening_amount + as_decimal(transactions.get(row.payment_method)))
		shift.append(
			"closing_amounts",
			{
				"payment_method": row.payment_method,
				"opening_amount": opening_amount,
				"closing_amount": closing.closing_amount if closing else 0,
				"expected_amount": expected,
			},
		)


def _set_shift_open(is_open):
	frappe.db.set_single_value("Books Pos Settings", "is_shift_open", int(is_open))
	profile = frappe.db.get_single_value("Books Pos Settings", "pos_profile")
	if profile:
		frappe.db.set_value(
			"Books Pos Profile", profile, "is_shift_open", int(is_open), update_modified=False
		)


def _open_shift_name():
	for name in frappe.get_all("Books Pos Opening Shift", order_by="opening_date desc", pluck="name"):
		if not frappe.db.exists("Books Pos Closing Shift", {"opening_shift": name}):
			return name
	return None


def _validate_cash_rows(rows):
	for row in rows:
		if as_decimal(row.denomination) <= 0 or int(row.count or 0) < 0:
			frappe.throw(_("Cash denominations must be positive and counts cannot be negative."))


def _amount_map(rows, value_field):
	result = {}
	for row in rows:
		if row.payment_method in result:
			frappe.throw(_("Payment method {0} is listed more than once.").format(row.payment_method))
		value = as_decimal(row.get(value_field))
		if value < 0:
			frappe.throw(_("POS amounts cannot be negative."))
		result[row.payment_method] = value
	return result


def _cash_total(rows):
	return rounded(sum((as_decimal(row.denomination) * int(row.count or 0) for row in rows), as_decimal(0)))


def _cash_account():
	if not frappe.db.exists("Books Account", "Cash"):
		frappe.throw(_("The standard Cash account is required for POS shifts."))
	return "Cash"


def _make_cash_journal(posting_date, rows, remark):
	if not rows or not any(as_decimal(debit) or as_decimal(credit) for _, debit, credit in rows):
		return
	journal = frappe.get_doc(
		{
			"doctype": "Books Journal Entry",
			"entry_type": "Cash Entry",
			"posting_date": frappe.utils.getdate(posting_date),
			"user_remark": remark,
			"accounts": [
				{"account": account, "debit": rounded(debit), "credit": rounded(credit)}
				for account, debit, credit in rows
				if as_decimal(debit) or as_decimal(credit)
			],
		}
	).insert(ignore_permissions=True)
	journal.submit()
