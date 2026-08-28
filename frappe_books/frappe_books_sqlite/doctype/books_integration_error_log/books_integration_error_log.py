# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BooksIntegrationErrorLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		data: DF.Text | None
		error: DF.Text | None
		name: DF.Int | None
		spacer: DF.Text | None
	# end: auto-generated types

	_DOCTYPE_NAME = "Books Integration Error Log"
