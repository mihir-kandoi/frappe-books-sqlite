# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BooksErpNextSyncSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		auth_token: DF.Password | None
		base_url: DF.Data | None
		clear_synced_docs_from_erp_next_sync_queue: DF.Data | None
		data_sync_interval: DF.Data | None
		device_id: DF.Data | None
		fetch_from_erp_next_queue: DF.Data | None
		initial_sync_data: DF.Check
		integration_app_version: DF.Data | None
		is_enabled: DF.Check
		register_instance: DF.Data | None
		sync_data_to_erp_next: DF.Data | None
		sync_settings: DF.Data | None
	# end: auto-generated types

	_DOCTYPE_NAME = "Books Erp Next Sync Settings"
