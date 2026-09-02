# Frappe Books for Frappe Framework and SQLite

This repository contains a pure Frappe Framework application for Books. It serves the Vue interface at `/books` and uses Frappe for authentication, permissions, document storage, and server workflows.

The app follows the standalone SPA structure used by ERPNext Banking. Vite writes generated assets to `frappe_books/public/books`, and a Frappe website page serves the generated entry point. The source repository does not store generated assets.

Frappe runs submit and cancel actions in one server transaction. This keeps ledger, stock, payment, pricing, and loyalty updates atomic. Draft updates also reject stale modification times.

The port targets Frappe Framework version 16. SQLite support in Frappe is still experimental. Use this app for local use, evaluation, and controlled single-site deployments. Test it carefully before you use it for production accounting data.

## Included

- Books Vue interface on the standalone `/books` route
- Standard Frappe DocTypes generated from the interface schemas
- Authenticated Frappe APIs for document operations and aggregate queries
- Setup wizard, standard chart of accounts, number series, roles, and defaults
- Sales invoices, purchase invoices, quotes, payments, journal entries, returns, and cancellation reversals
- Quote-to-invoice, invoice-to-payment, and invoice-to-return Desk actions
- Inventory ledger, FIFO valuation, stock movements, shipments, receipts, batches, and serial numbers
- Automatic shipment or receipt creation from invoices
- POS shifts and checkout, split-payment API support, pricing rules, coupons, and loyalty points
- India GST fields and GSTR-1/GSTR-2 reports, plus Swiss regional schema fields
- General Ledger, Trial Balance, Profit and Loss, Balance Sheet, Stock Ledger, and Stock Balance reports
- Native Frappe print formats for invoices, quotes, payments, shipments, and receipts
- Dashboard, POS, Books workspace, and Data Import/Data Export links

The browser handles downloads, file selection, and printing. Company data belongs to the current Frappe site. The app does not contain a local company-database selector, device telemetry, an updater, or an ERPNext device-sync client.

## Requirements

- Frappe Framework 16
- Python 3.14
- Redis
- SQLite 3

This app does not require MariaDB or PostgreSQL. It is not intended for Frappe Cloud.

Production installation requires Node.js and Yarn. Bench installs the frontend dependencies and builds the Vue app during deployment.

The repository stores the Vue source and its lockfile. It does not store generated JavaScript, CSS, or the generated Frappe website entry.

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

## Build the web app

Install the frontend dependencies from the app root:

```bash
yarn install
```

Build the production assets:

```bash
yarn build
```

Vite writes the asset graph to `frappe_books/public/books`. The build then copies the generated HTML entry to `frappe_books/www/books.html`.

Bench uses the root `build` script during `bench build --app frappe_books`. This follows the same source-to-generated-output pattern as ERPNext Banking.

The app also keeps these Desk routes for administration:

- `/app/books` — Books workspace
- `/app/books-dashboard` — dashboard
- `/app/books-pos` — point of sale

Use standard Frappe **Data Import** and **Data Export** for CSV-based transfers.

## Schema synchronization

The checked-in DocTypes and `frappe_books/schema_mapping.json` are generated from the frontend schema files. After you change a frontend schema, synchronize it from the bench:

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

The integration suite covers the UI data layer, posting, reversals, payments, reports, stock, POS, setup, and printing.

## SQLite operations

Frappe stores the database file under `sites/<site>/db/`. Back up the complete site, including `site_config.json`, private files, public files, and the SQLite database file.

SQLite serializes writes to one database file. Run one web deployment for a site unless you have tested its write workload and locking behavior. Keep the database on a local persistent volume, not a network file system. Stop writers or use Frappe's backup command when you take a filesystem-level copy.

After updating this app, always run:

```bash
bench --site books-sqlite.localhost migrate
```

## License

AGPL-3.0-only
