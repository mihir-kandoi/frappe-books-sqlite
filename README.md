# Frappe Books for Frappe Framework and SQLite

This app runs the original Frappe Books Vue interface at `/books`. It uses Frappe authentication, permissions, APIs, and SQLite storage.

The interface reuses the desktop components, routes, forms, lists, reports, and setup wizard. A compatibility layer replaces the Electron database and IPC calls. The app follows the standalone SPA structure used by ERPNext Banking. Vite writes assets to `public/books` and a Frappe website page serves them.

Frappe runs submit and cancel actions in one server transaction. This keeps ledger, stock, payment, pricing, and loyalty updates atomic. Draft updates also reject stale modification times.

The port targets Frappe Framework version 16. SQLite support in Frappe is still experimental. Use this app for local use, evaluation, and controlled single-site deployments. Test it carefully before you use it for production accounting data.

## Included

- Original Frappe Books Vue interface on the standalone `/books` route
- 74 standard Frappe DocTypes generated from the desktop Books schemas
- Authenticated API bridge for the desktop database contract and dashboard queries
- Setup wizard, standard chart of accounts, number series, roles, and defaults
- Sales invoices, purchase invoices, quotes, payments, journal entries, returns, and cancellation reversals
- Quote-to-invoice, invoice-to-payment, and invoice-to-return Desk actions
- Inventory ledger, FIFO valuation, stock movements, shipments, receipts, batches, and serial numbers
- Automatic shipment or receipt creation from invoices
- POS shifts and checkout, split-payment API support, pricing rules, coupons, and loyalty points
- India GST fields and GSTR-1/GSTR-2 reports, plus Swiss regional schema fields
- General Ledger, Trial Balance, Profit and Loss, Balance Sheet, Stock Ledger, and Stock Balance reports
- Native Frappe print formats for invoices, quotes, payments, shipments, and receipts
- Dashboard, POS, Books workspace, Data Import/Data Export links, and a desktop SQLite database importer

The Electron runtime is not part of this app. The browser handles downloads, file selection, and printing. Window controls and automatic desktop updates do nothing. The old `books_integration` device-sync client is not active. Imported sync records remain available, but remote ERPNext sync needs a separate connector.

## Requirements

- Frappe Framework 16
- Python 3.14
- Redis
- SQLite 3

This app does not require MariaDB or PostgreSQL. It is not intended for Frappe Cloud.

The repository includes the built Vue assets. You do not need Node.js or Yarn to install the app.

## Install the app

Install Python and Bench:

```bash
uv python install 3.14
uv tool install frappe-bench
```

Create a Frappe v16 bench outside this repository:

```bash
BOOKS_PYTHON="$(uv python find 3.14)"
bench init --frappe-branch version-16 --python "$BOOKS_PYTHON" books-frappe-sqlite-bench
cd books-frappe-sqlite-bench
```

Install the app from GitHub:

```bash
bench get-app https://github.com/mihir-kandoi/frappe-books-sqlite.git
bench set-config -g developer_mode 1
```

Create and install a SQLite site:

```bash
bench new-site books-sqlite.localhost \
  --db-type sqlite \
  --admin-password admin \
  --set-default
bench --site books-sqlite.localhost install-app frappe_books
bench --site books-sqlite.localhost migrate
bench start
```

Open `http://books-sqlite.localhost:8000/books`. Sign in and complete the original Books setup wizard.

The app also keeps these Desk routes for administration and migration:

- `/app/books` — Books workspace
- `/app/books-dashboard` — dashboard
- `/app/books-pos` — point of sale
- `/app/books-desktop-import` — desktop database import

## Import a desktop Books company

Make a backup of the desktop `.books.db` file. Import into a fresh site when possible.

1. Open **Books > Settings and Data > Import Desktop Database**.
2. Upload the `.books.db`, `.db`, `.sqlite`, or `.sqlite3` file.
3. Review the integrity check and mapped row counts.
4. Confirm the import.

The importer opens the source database read-only. It preserves document names, audit fields, children, settings, and submitted or cancelled status. It deliberately bypasses submit hooks because the desktop database already contains ledger rows. A repeated import skips records that already exist.

Use standard Frappe **Data Import** and **Data Export** for CSV-based transfers.

## Schema synchronization

The checked-in DocTypes and `frappe_books/schema_mapping.json` are generated from the desktop schema files. After changing a desktop schema, synchronize it from the bench:

```bash
bench --site books-sqlite.localhost execute frappe_books.dev.schema_sync.sync \
  --kwargs '{"source_root":"/absolute/path/to/books"}'
bench --site books-sqlite.localhost migrate
```

Review generated files before committing them. Keep application logic outside the auto-generated type blocks in DocType controllers.

## Tests and checks

Use a separate SQLite site for tests:

```bash
bench new-site books-sqlite-test.localhost \
  --db-type sqlite \
  --admin-password admin
bench --site books-sqlite-test.localhost install-app frappe_books
bench --site books-sqlite-test.localhost set-config allow_tests 1 --parse
bench --site books-sqlite-test.localhost migrate
bench --site books-sqlite-test.localhost run-tests --app frappe_books
uvx ruff check apps/frappe_books/frappe_books
uvx ruff format --check apps/frappe_books/frappe_books
```

The integration suite covers the UI bridge, posting, reversals, payments, reports, stock, POS, setup, printing, and desktop database import.

## SQLite operations

Frappe stores the database file under `sites/<site>/db/`. Back up the complete site, including `site_config.json`, private files, public files, and the SQLite database file.

SQLite serializes writes to one database file. Run one web deployment for a site unless you have tested its write workload and locking behavior. Keep the database on a local persistent volume, not a network file system. Stop writers or use Frappe's backup command when you take a filesystem-level copy.

After updating this app, always run:

```bash
bench --site books-sqlite.localhost migrate
```

## License

AGPL-3.0-only
