# RecordForge

### Generate realistic test files in seconds. No fake data leaks.

A Windows desktop app and Python package by [Michael Nocito](https://www.linkedin.com/in/michaelnocito).

**[🌐 recordforge website](https://michaelnocito.github.io/recordforge/)** &nbsp;·&nbsp; [Releases](https://github.com/michaelnocito/recordforge/releases) &nbsp;·&nbsp; [Troubleshooting](docs/TROUBLESHOOTING.md)

<!--
VISUAL PLACEMENT 1 — Hero banner
Future path: docs/images/hero-banner.png
Alt text: RecordForge — fictional PDFs, Word docs, HTML, and Excel for QA and demos
To create: a wide hero banner (~1600×500). Left side shows stacked
sample outputs (an invoice PDF, a contract Word doc, and an Excel
sheet with customer rows); right side shows the 3-step wizard UI
(Mode & Type → Settings → Generate). Project name + tagline overlaid.
When ready, replace this comment with:
![RecordForge — fictional PDFs, Word docs, HTML, and Excel for QA and demos](docs/images/hero-banner.png)
-->

---

> ⚠️ All output is synthetic and fictional. Never use for legal, financial, medical, regulatory, or identity purposes.

You can generate a folder full of realistic — but completely fictional —
business documents and data sets in a few clicks. Invoices, purchase
orders, contracts, offer letters, customer records, transactions, even
intentionally messy spreadsheets for cleanup drills.

Pick what you need, how many, and where to save them. The app handles
the rest. You end up with test files you can drop straight into a QA
run, a demo, or a training session — no real customer data involved.

---

## Two Ways to Use It

Pick whichever fits you. Both produce the same files.

- **Desktop app (Windows installer)** — You can run it without Python.
  Download, click, generate files. Jump to
  [Download & Install](#%EF%B8%8F-download--install-windows).
- **Python package** — Install with pip, use the CLI or the Python API,
  extend it with your own types.
  Jump to [Run from Python](#run-from-python-developers).

---

## See It In Action

Open the app and you get a 3-step wizard: pick your file types, choose
how many and what format, then generate. Names, addresses, and party
details are randomized for every file. Output lands in the folder you
choose, and you can open any file directly from the app the moment it
finishes.

<!--
VISUAL PLACEMENT 2 — Product screenshot or short GIF
Future path: docs/images/wizard.png (or wizard.gif)
Alt text: 3-step wizard generating fictional PDFs and Excel data files
To create: a screenshot or 8–12s GIF of the running app showing
the Mode & Type → Settings → Generate flow. End on the success
state with the generated file list visible. PNG is fine; GIF is
better if easy to record.
When ready, replace this comment with:
![3-step wizard generating fictional PDFs and Excel data files](docs/images/wizard.png)
-->

---

## ⬇️ Download & Install (Windows)

1. Go to [**Releases**](https://github.com/michaelnocito/recordforge/releases/latest)
2. Download `RecordForgeSetup.exe`
3. Double-click the installer and follow the wizard (Next → Next → Finish)
4. Launch from the **Desktop shortcut** or **Start Menu**

You do not need Python for this path. Works on Windows 10 and Windows 11.

> **Blank white screen after launch?** Your machine may be missing the
> Microsoft Edge WebView2 Runtime — this is required by the app.
> [Download it free from Microsoft](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)
> and reinstall. See [Troubleshooting](docs/TROUBLESHOOTING.md) for more help.

---

## How It Works

Three steps, one folder of test files at the end.

<!--
VISUAL PLACEMENT 3 — Simple workflow diagram
Future path: docs/images/workflow.svg (preferred) or docs/images/workflow.png
Alt text: Choose file types and settings, generate fictional documents and data, use in QA demos and training
To create: a clean horizontal flow diagram showing:
  [Choose Types & Format] → [Generate Fictional Files] → [Use in QA / Demo / Training]
Keep it friendly and non-technical. Use simple icons for each stage
(checklist → gear/sparkle → laptop/clipboard). Excalidraw, Figma, or
a clean Keynote/PowerPoint export works well.
When ready, replace this comment with:
![Choose file types and settings, generate fictional documents and data, use in QA demos and training](docs/images/workflow.svg)
-->

**Step 1 — Mode & Type**
- Choose **Documents**, **Data Files**, or **Both**
- Select the types you want (pick as many as you need)

**Step 2 — Settings**
- Set how many files per type (1–20)
- Choose a document format: **PDF**, **Word .docx**, or **HTML**
  - Skip this if you are only generating data files
- Set your output folder (defaults to `~/Documents/recordforge`)

**Step 3 — Review & Generate**
- Confirm your selections in the summary
- Click **Generate Test Files**
- Click any file or **Open Output Folder** when done

---

## What You Can Generate

**Documents** (PDF / Word `.docx` / HTML)

- Invoice
- Purchase Order
- Intake Form
- SOP
- Contract
- Offer Letter

**Data files** (Excel `.xlsx` / CSV / JSON / JSONL in the app; **SQL** and **Parquet** also available from the CLI, with a configurable number of rows per file)

- Customer Records
- Vendor Master
- Transactions
- Employee Records
- Inventory
- Payments — checksum-valid but fake cards (Luhn), IBANs (mod-97), and non-routable routing numbers (ABA), for testing payment validators
- Messy Data — nulls, duplicates, bad formatting (great for cleanup testing)
- Edge Cases — an adversarial corpus (boundaries, unicode, injection, bad dates) for stress-testing parsers and validators

**Linked data that actually joins (new in v2.1.0)**

Generate several tables at once with real foreign keys, so the rows join with
no orphans. This is the part no cloud-free, offline generator usually does.

- **Relational bundle** (`recordforge generate-related`): customers,
  transactions, and payments generated together, where every transaction
  belongs to a real customer and every payment settles a real transaction.
- **Your own schema** (`recordforge generate-schema`): describe your tables,
  columns, and relationships in a small YAML or JSON file. RecordForge builds
  them in the correct order, handles self-references (like an employee's
  manager), and refuses impossible loops with a clear message. Ready-made
  examples live in [`examples/`](examples/).
- **SQL and Parquet output**: export to ready-to-run `INSERT` statements
  (written parents-first so they load without breaking foreign keys) or to
  Parquet for data-engineering workflows. Parquet needs the optional
  `pip install "recordforge[parquet]"` and is kept out of the desktop
  installer to keep it small.

Every org name, address, contact, and party detail is randomly generated
per file. Pick an output folder, then open files directly from the app
when generation finishes.

---

## Who This Is For

- **QA engineers** who want varied, realistic test files without scrubbing real data
- **Sales and solutions teams** building demos that can't use customer documents
- **Trainers and bootcamps** running data-cleaning, document-processing, or migration exercises
- **Developers** testing import pipelines, OCR, parsers, or doc workflows on safe sample data

If you build, test, or teach with documents and data, you can use this
to skip the busywork of hand-crafting sample files and focus on the
work that matters.

---

## Run from Python (Developers)

Requires Python 3.11+ and pip.

```powershell
git clone https://github.com/michaelnocito/recordforge.git
cd recordforge
pip install -e .
```

**CLI:**

```
recordforge generate --type invoice --format pdf --count 5
recordforge generate --type customers --format csv --rows 500
recordforge generate --type transactions --format jsonl --rows 10000 --seed 42
recordforge generate --type customers --format csv --rows 200 --dirty "nulls=0.1,case_drift=0.2,duplicates=0.05"
recordforge generate --type customers --format parquet --rows 1000
recordforge generate-related --format csv --customers 100 --transactions 500 --payments 200
recordforge generate-schema --schema examples/shop.yml --format sql --seed 1
recordforge list-types
```

Data types accept `--format xlsx | csv | json | jsonl | sql | parquet` and
`--rows` (records per file). Document types accept `--format pdf | docx | html`.
`generate-related` and `generate-schema` produce linked tables with real foreign
keys; with `--format sql` they write a single, foreign-key-ordered `.sql` file.

**Induce errors on purpose** with `--dirty` (or the "Induce errors" menu in the
app) to test data-cleaning pipelines: choose any of `nulls`, `blanks`,
`whitespace`, `case_drift`, `format_drift`, `outliers`, `encoding`, `duplicates`,
each at a rate you set.

**Python API:**

```python
from recordforge import generate, generate_related, generate_schema

# One document/data type at a time
docs = generate(type="invoice", format="pdf", count=3, output="./out")
for doc in docs:
    print(doc.path)

# Linked tables with real foreign keys, no orphans
generate_related(output="./out", format="csv", customers=100, transactions=500, payments=200)

# Your own tables and relationships from a schema file
generate_schema("examples/shop.yml", output="./out", format="sql", seed=1)
```

**Desktop UI:**

```
python -m recordforge
```

To build your own EXE or installer, see [INSTALL.md](INSTALL.md).

---

## Project Structure

```text
recordforge/
├── recordforge/
│   ├── __init__.py              ← public Python API (generate, generate_related, generate_schema, list_types, set_seed)
│   ├── __main__.py              ← python -m recordforge → desktop UI
│   ├── cli.py                   ← Typer CLI (generate, generate-related, generate-schema, list-types)
│   ├── core/                    ← models, RNG, faker helpers, watermark engine
│   ├── generators/
│   │   ├── documents/           ← one module per document type
│   │   ├── data/                ← one module per data type
│   │   └── related.py           ← built-in customers→transactions→payments bundle
│   ├── schema/                  ← YAML/JSON schema loader, column types, FK graph + build engine
│   ├── renderers/               ← pdf, docx, html, xlsx, csv, json, jsonl, sql, parquet
│   └── ui/                      ← pywebview API bridge + wizard HTML
├── examples/                    ← sample schema files (shop.yml, org.json)
├── tests/
│   └── test_smoke.py
├── installer.iss                ← Inno Setup script
├── requirements.txt
├── pyproject.toml
└── INSTALL.md                   ← EXE + installer build instructions
```

---

## Safety & Privacy

- No real personal data is ever used in generated output
- Generation is fully offline — nothing you create ever leaves your machine, no telemetry, no account. The app's only network request is the opt-in **Check for Updates** button, which reads the public Releases list to compare version numbers and sends no personal data
- User-entered output folder paths are not stored or transmitted
- Generated files stay on your machine in the folder you choose
- See [PRIVACY.md](PRIVACY.md) for full details

---

## Need Help?

- [Installation & Build Guide](INSTALL.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Changelog](CHANGELOG.md)
- [Contributing](docs/CONTRIBUTING.md)

---

## More from Michael Nocito

**[🕵️ NEXUS — Learn SQL by Solving a Mystery](https://michaelnocito.github.io/nexus-sql-mystery/)** —
A free game where you investigate corporate fraud by writing real SQL against a live database.
No slides, no exercises — every query is evidence. Two full seasons.

**[📊 Analyst Prep Kit](https://michaelnocito.github.io/analyst-prep-kit/)** —
A free browser-based suite for breaking into data analytics — SQL, Excel, Python, Tableau, and Statistics.
12 lessons per module, real in-browser environments, honest readiness score. No install, no login.

**[🧼 Spreadsheet Cleaner](https://michaelnocito.github.io/spreadsheet-cleaner/)** —
A beginner Python project where you build a real data-cleaning tool layer by layer.
The Messy Data output from RecordForge pairs directly with this cleaner.

**[LinkedIn](https://www.linkedin.com/in/michaelnocito)** — data analyst · 8 years enterprise implementation

---

If this project saved you time, the best thing you can do is
[⭐ star the repo](https://github.com/michaelnocito/recordforge)
— it helps others find it.

If you'd like to support the work, a coffee is always appreciated but never expected.

<a href="https://buymeacoffee.com/michaelnocito" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50">
</a>

---

Built with 🐍 Python | Maintained by [Michael Nocito](https://github.com/michaelnocito)
