# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BooksFetchFromErpNextQueue(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		document_name: DF.Data
		reference_type: DF.Literal[
			"Item",
			"Party",
			"SalesInvoice",
			"POSClosingShift",
			"POSOpeningShift",
			"Payment",
			"StockMovement",
			"PriceList",
			"SerialNumber",
			"Batch",
			"UOM",
			"Address",
		]
	# end: auto-generated types

	_DOCTYPE_NAME = "Books Fetch From Erp Next Queue"
