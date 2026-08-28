# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BooksCustomForm(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from frappe_books.frappe_books_sqlite.doctype.books_custom_field.books_custom_field import (
			BooksCustomField,
		)

		custom_fields: DF.Table[BooksCustomField]
	# end: auto-generated types

	_DOCTYPE_NAME = "Books Custom Form"
