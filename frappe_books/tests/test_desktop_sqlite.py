"""Integration coverage for desktop SQLite migration."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import frappe
from frappe.tests import IntegrationTestCase

from frappe_books.migration.desktop_sqlite import DesktopDatabase, import_database
from frappe_books.tests.accounting import unique_name


class IntegrationTestDesktopSQLiteImport(IntegrationTestCase):
	def test_preview_and_import_preserve_transactions(self):
		account = unique_name("Imported Receivable")
		party = unique_name("Imported Customer")
		invoice = unique_name("SINV-IMPORTED")
		item = unique_name("Imported Item")
		child = unique_name("Imported Invoice Item")
		company = unique_name("Imported Company")
		path = self._database(
			account=account,
			party=party,
			invoice=invoice,
			item=item,
			child=child,
			company=company,
		)

		with DesktopDatabase(path) as source:
			preview = source.preview()
		self.assertEqual(preview["counts"]["SalesInvoice"], 1)
		self.assertEqual(preview["single_values"], 2)

		result = import_database(path)
		self.assertEqual(result["inserted"]["Books Sales Invoice"], 1)
		self.assertEqual(result["single_values"], 2)

		imported = frappe.get_doc("Books Sales Invoice", invoice)
		self.assertEqual(imported.docstatus, 1)
		self.assertEqual(imported.party, party)
		self.assertEqual(len(imported.items), 1)
		self.assertEqual(imported.items[0].name, child)
		self.assertEqual(imported.items[0].item, item)
		self.assertEqual(imported.items[0].quantity, 2)
		self.assertEqual(
			frappe.db.get_single_value("Books Accounting Settings", "company_name"),
			company,
		)

		second = import_database(path)
		self.assertEqual(second["skipped"]["Books Sales Invoice"], 1)

	def _database(self, **values: str) -> Path:
		handle = tempfile.NamedTemporaryFile(suffix=".books.db", delete=False)
		path = Path(handle.name)
		handle.close()
		self.addCleanup(lambda: path.unlink(missing_ok=True))

		with sqlite3.connect(path) as connection:
			connection.executescript(
				"""
				create table SingleValue (
					name text primary key, parent text, fieldname text, value text
				);
				create table Account (
					name text primary key, rootType text, parentAccount text,
					accountType text, isGroup integer, createdBy text, modifiedBy text,
					created text, modified text
				);
				create table Party (
					name text primary key, role text, defaultAccount text
				);
				create table Item (
					name text primary key, itemCode text, itemUsage text, unit text,
					incomeAccount text, expenseAccount text
				);
				create table SalesInvoice (
					name text primary key, numberSeries text, party text, account text,
					date text, netTotal real, baseGrandTotal real, grandTotal real,
					outstandingAmount real, submitted integer, cancelled integer,
					createdBy text, modifiedBy text, created text, modified text
				);
				create table SalesInvoiceItem (
					name text primary key, parent text, parentSchemaName text,
					parentFieldname text, idx integer, item text, itemCode text,
					quantity real, rate real, amount real
				);
				"""
			)
			timestamp = "2026-08-27T10:00:00.000Z"
			connection.execute(
				"insert into Account values (?, 'Asset', null, 'Receivable', 0, ?, ?, ?, ?)",
				(values["account"], "__SYSTEM__", "__SYSTEM__", timestamp, timestamp),
			)
			connection.execute(
				"insert into Party values (?, 'Customer', ?)",
				(values["party"], values["account"]),
			)
			connection.execute(
				"insert into Item values (?, ?, 'Both', 'Unit', ?, ?)",
				(values["item"], values["item"], values["account"], values["account"]),
			)
			connection.execute(
				"""insert into SalesInvoice values (
					?, 'SINV-', ?, ?, ?, 200, 200, 200, 200, 1, 0, ?, ?, ?, ?
				)""",
				(
					values["invoice"],
					values["party"],
					values["account"],
					timestamp,
					"__SYSTEM__",
					"__SYSTEM__",
					timestamp,
					timestamp,
				),
			)
			connection.execute(
				"""insert into SalesInvoiceItem values (
					?, ?, 'SalesInvoice', 'items', 1, ?, ?, 2, 100, 200
				)""",
				(values["child"], values["invoice"], values["item"], values["item"]),
			)
			connection.executemany(
				"insert into SingleValue values (?, 'AccountingSettings', ?, ?)",
				(
					(unique_name("single"), "companyName", values["company"]),
					(unique_name("single"), "enableInventory", "1"),
				),
			)
		return path
