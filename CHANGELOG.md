# Changelog

All notable changes to this project are documented here.

---

## [Unreleased]

## [2.1.0] — 2026-07-19

### New data formats — SQL and Parquet (Phase C, slice C3)

- **SQL INSERT renderer** (`renderers/sql.py`, Postgres / ANSI flavor): emits
  `INSERT INTO` statements with double-quoted identifiers and standard
  single-quote escaping, batched into multi-row `VALUES`. Available as
  `--format sql` on `generate`, `generate-related`, and `generate-schema`
- For relational bundles and schemas, SQL is written as **one combined .sql
  file with tables in foreign-key-safe order** (parents before children, via
  the schema's topological order), so it loads into a database without
  violating foreign keys. Verified by loading a generated bundle into SQLite
  and confirming the joins resolve with no orphans. Output is deterministic
  (no timestamps), so a seeded run reproduces byte for byte
- **Parquet renderer** (`renderers/parquet.py`, via `pyarrow`): `--format
  parquet` on the same three commands. Columns that mix types (such as the
  `edge_cases` corpus) fall back to text so any dataset still writes a valid
  file
- `pyarrow` is an **optional extra** (`pip install "recordforge[parquet]"`),
  imported lazily and deliberately **not bundled in the Windows installer** to
  keep it lean. Importing `recordforge` does not import `pyarrow`; selecting
  Parquet without it gives a clear install message. The desktop app's format
  picker is unchanged (xlsx/csv/json/jsonl), so SQL and Parquet are pip/CLI
  features

### Referential integrity — schema files (Phase C, slice C2)

- New `recordforge/schema/` package: define **datasets, columns, and foreign-key
  relationships in a YAML or JSON file**, then generate all of them at once with
  referential integrity. Foreign keys resolve to real parent keys, so the output
  joins with no orphans
- Column type vocabulary: `id` (sequential key), `fk` (foreign key ->
  `table.column`), `person`, `company`, `email`, `phone`, `int`, `decimal`,
  `money`, `choice`, `date`, `bool`, `string`, `card`, `iban`,
  `routing_number`, `account_number`
- Builds a **dependency graph and topological (parent-before-child) insert
  order**, keeps per-column **key pools** for foreign keys to draw from, and
  handles **self-references** (for example `manager_id -> employees.employee_id`)
  as an acyclic hierarchy: the first row is a null root and every later row
  points at an earlier one, so there is never a cycle
- A true cross-table circular dependency is reported as a clear error, not
  silently mis-generated
- Schema validation runs before any file is written, with errors that name the
  offending dataset and column (unknown type, foreign key to a missing
  table/column, `choice` without values, and so on)
- New public API `generate_schema(schema_path, output, format, seed)` and CLI
  `recordforge generate-schema --schema shop.yml --format csv [--seed N]
  [--output DIR]`
- Example schemas under `examples/`: `shop.yml` (customers -> orders ->
  order_payments) and `org.json` (departments + a self-referencing employee
  hierarchy)
- Adds a `pyyaml` dependency for reading YAML schemas (pure-Python, offline;
  JSON schemas need no extra dependency)

### Referential integrity — relational bundle (Phase C, slice C1)

- New `generators/related.py` builds **customers, transactions, and payments in
  one pass with real foreign keys**: every `transactions.customer_id` is drawn
  from the generated `customers.customer_id` pool, and every payment settles a
  real transaction (inheriting its `txn_id`, `customer_id`, `amount`, and
  `currency`, and naming the matching customer as `account_holder`). Parents are
  built before children, so the output never contains an orphan foreign key
- New public API `generate_related(output, format, seed, customers,
  transactions, payments)` renders each dataset to a chosen data format in
  dependency order; returns one `GeneratedDoc` per dataset
- New CLI `recordforge generate-related --format csv --customers 100
  --transactions 500 --payments 200 [--seed N] [--output DIR]`
- Deterministic under a seed and fully offline, like every other generator

### Fixed
- XLSX renderer no longer crashes on control characters (e.g. the `edge_cases`
  null-byte value): characters Excel cannot store are escaped to their `\xNN`
  text form. CSV/JSON keep the raw bytes.

### Data Forge — checksum-valid identifiers (Phase B)

- New checksum helpers in `core/faker_utils.py`: `rand_card` (Luhn-valid card
  numbers in test BIN ranges), `rand_iban` (mod-97-valid IBANs for DE/ES/NL),
  `rand_routing_number` (ABA-checksum-valid but **non-routable** — "99" prefix,
  an unassigned Federal Reserve routing symbol), and `rand_account_number`
- New `payments` data type using them (schema: `payment_id, account_holder,
  card_brand, card_number, iban, routing_number, account_number, amount,
  currency`)
- These pass format validators in a test pipeline while never being real
  accounts — fake by construction, safe to generate openly

### Data Forge — edge-case corpus (Phase B)

- New `edge_cases` data type: a labeled adversarial corpus (schema
  `edge_id, category, label, value`) covering integer/float boundaries, empty
  and whitespace strings, very long strings, unicode stress (emoji, combining
  marks, RTL, zero-width, CJK, null bytes), injection payloads (SQL, XSS,
  template, log4shell, path traversal, spreadsheet-formula), extreme/invalid
  dates, special numbers, null-like tokens, and CSV-breaking delimiters
- Interleaved by category so even a small `--rows` count spans many categories;
  cycles when `--rows` exceeds the pool
- Deterministic and offline (a curated subset inspired by the Big List of
  Naughty Strings, kept inline — no bundled megafile, no download)
- Available in the CLI, API, and the desktop app's data-type picker

### Data Forge — a-la-carte "dirty data" (Phase B)

- New `core/dirty.py`: a post-generation transform that injects **user-chosen**
  errors into any dataset, at a controllable rate. Pick which problems to induce:
  `nulls`, `blanks`, `whitespace`, `case_drift`, `format_drift`, `outliers`,
  `encoding` (mojibake), `duplicates`
- Fully deterministic under a seed; transforms run in a fixed order and never
  mutate the caller's rows
- API: new `dirty` parameter on `generate()` (a `{type: rate}` dict)
- CLI: new `--dirty` option, e.g. `--dirty "nulls=0.1,case_drift=0.2,duplicates=0.05"`;
  `list-types` now lists the available error types
- Desktop app: an "Induce errors" menu in Step 2 (error checkboxes + Light/Medium/
  Heavy intensity), shown for data and both modes; the review summarizes it
- Great for testing data-cleaning / validation pipelines and for cleanup drills

### Data Forge — formats and row control (Phase B)

**Data output formats**
- Data types now export to **CSV, JSON, and JSONL** in addition to Excel `.xlsx`
- New renderers: `renderers/csv.py`, `renderers/json.py`, `renderers/jsonl.py`
- Output is clean and directly loadable (no injected disclaimer rows that would
  break parsing); None values and Decimals serialize safely

**Rows per file**
- New `rows` parameter on `generate()` controls records per data file
  (previously fixed at ~50); clamped 1–1,000,000
- CLI: new `--rows` option
- Desktop app: data format selector (Excel / CSV / JSON / JSONL) and a
  "Rows per file" input in Step 2, shown for data and both modes

**Seed in the desktop app**
- Step 2 now has an optional "Seed" field for reproducible output (the CLI
  and API already had `--seed` / `seed=`)
- The whole batch is seeded once, so files are deterministic yet still vary
  across types and copies

**Tests**
- 29 smoke tests (up from 21): new-format round-trips, row-count control,
  format validation, and cross-format seed reproducibility

---

## [2.0.0] — 2026-05-18

### RecordForge — full refactor and rename

**Package**
- Refactored v1 monolith (`main.py`) into a proper Python package (`recordforge/`)
- Installable via `pip install -e .` from repo root
- Public Python API: `from recordforge import generate, list_types, set_seed`
- Typer CLI: `recordforge generate`, `recordforge list-types`, `recordforge version`
- Desktop UI launcher: `python -m recordforge`

**PDF renderer**
- Replaced raw canvas line-by-line output with `reportlab.platypus` layout engine
- Full document layout: header block, two-column party block, line items table with alternating shading, computed totals (subtotal / tax / Total Due)
- Diagonal SAMPLE watermark on every page (72pt Helvetica-Bold, red, 15% opacity)
- Footer disclaimer on every page

**DOCX renderer**
- Upgraded from plain paragraphs to structured layout
- Two-column borderless party table, styled line items table with header row and totals

**HTML renderer**
- Replaced f-string HTML with Jinja2 template (`renderers/templates/document.html.j2`)
- CSS diagonal SAMPLE watermark via `body::before`

**Generators**
- All 6 document types and 6 data types refactored into individual modules
- Relational integrity: `doc_date` always before `due_date`
- All financial values computed from `LineItem` dataclasses — no hardcoded dollar strings
- Faker word lists expanded to 40+ entries each (vs. 10 in v1)
- Seed control: `set_seed(n)` produces fully reproducible output

**Core**
- `core/models.py` — typed dataclasses: `Party`, `LineItem`, `DocumentData`, `GeneratedDoc`
- `core/seed.py` — shared RNG singleton, no global random calls anywhere
- `core/faker_utils.py` — all `rand_*` helpers, expanded word lists
- `core/watermark.py` — watermark engine decoupled from renderer

**Tests**
- 21 smoke tests: all generators, all renderers, watermark presence, seed reproducibility

---

## [1.0.0] — 2026-05-12

### First stable release

**App**
- 3-step wizard UI (Mode & Type → Settings → Generate)
- pywebview desktop window loads `ui.html` via `html=` parameter
- `debug=False` for clean production window

**Document generation**
- Invoice, Purchase Order, Intake Form, SOP, Contract, Offer Letter
- Export formats: PDF (ReportLab), Word .docx (python-docx), HTML
- All party / org data randomly generated

**Data generation**
- Customer Records, Vendor Master, Transactions, Employee Records, Inventory, Messy Data
- All data types export as Excel `.xlsx` (openpyxl)
- Messy Data includes nulls, duplicates, inconsistent casing for cleanup testing

**Output**
- Native folder picker dialog
- Open individual files or output folder directly from the app
- Random hex token in filenames prevents overwriting

**Distribution**
- Windows installer built with Inno Setup
- Start Menu and Desktop shortcuts created on install
- Standalone `.exe` also available via PyInstaller

**Safety**
- Disclaimer row in every Excel file
- Disclaimer block in every document
- Fully offline — no network calls

---

## Upcoming

See `ROADMAP.md` for the full plan. Near-term (Phase B/C):

- Schema files + referential integrity across datasets (foreign keys that join)
- SQL INSERT and Parquet output
- Additional document types (bank statement, pay stub, remittance, W-2/1099)
