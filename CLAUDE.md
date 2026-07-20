# CLAUDE.md — RecordForge

Rules for Claude Code. Read this before touching any file.

---

## Project

Python package that generates synthetic documents and data files for
data engineering and ETL testing. See SPEC.md for full architecture.

---

## Non-Negotiable Rules

1. **Read SPEC.md first.** Every architectural decision is already made.
   Do not invent structure not in the spec.

2. **No monoliths.** Every module has one job. If a function is growing
   past ~40 lines, it probably belongs in a different module.

3. **No global mutable state.** All randomness flows through the `rng`
   parameter. Never call `random.random()`, `random.choice()`, or any
   `random` module global directly. Always use the instance from
   `core/seed.py`.

4. **No hardcoded dollar amounts or strings in generators.** All
   financial values must be computed from `LineItem` dataclasses.
   "Implementation Services ... $12,500" is a v1 bug, not a feature.

5. **Watermark on every PDF page.** Non-negotiable. See SPEC.md watermark
   spec. Test this with multi-page outputs.

6. **Never break the existing UI contract.** The pywebview `generate()`
   method in `ui/app.py` must return the same JSON shape as v1:
   `{"success": bool, "files": list[str], "folder": str}` or
   `{"success": false, "error": str, "files": []}`.

---

## Python Style

- Python 3.11+ features are fine: `X | Y` unions, `match`, `tomllib`.
- Type hints on every function signature — parameters and return type.
- Dataclasses for all data models (`@dataclass`, not dicts, not
  namedtuples).
- `Decimal` for all currency math. Never `float` for money.
- `pathlib.Path` everywhere. Never `os.path.join`.
- f-strings for all string formatting.
- No `print()` in library code. CLI output goes through Typer's echo.
  UI output goes through the pywebview return value.
- Imports: stdlib → third-party → local, one blank line between groups.
- No wildcard imports (`from x import *`).

---

## File / Naming Conventions

- Module names: `snake_case`
- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Type aliases: `PascalCase`

---

## Error Handling

- All `generate()` paths (CLI, API, UI) must catch exceptions and
  return/raise cleanly — never let a stack trace reach the user
  without a message.
- Validation errors (bad type, bad format combo) should raise
  `ValueError` with a clear message before any file I/O starts.
- File I/O errors should be caught and reported with the failing path.

---

## Testing

- Write at minimum one smoke test per generator module:
  `build(rng)` returns a valid `DocumentData` instance.
- Write one test per renderer: output file exists and is non-empty.
- Write one test for watermark: PDF contains the string "SAMPLE" when
  read back as text (use `pdfminer` or `pypdf` if needed, or just check
  file size is non-trivial).
- Seed tests: same seed → same output filename stem and same line item
  totals.
- Test file: `tests/test_smoke.py` (single file for Phase A).

---

## What to Preserve from v1 (Do Not Refactor)

- `sanitize_filename()` — copy exactly, do not change behavior.
- `open_path()` platform detection — copy exactly.
- XLSX auto-width column logic.
- All 6 document type keys (strings must match exactly):
  `invoice`, `purchase_order`, `intake_form`, `sop`, `contract`,
  `offer_letter`
- All 6 data type keys:
  `customers`, `vendors`, `transactions`, `employees`, `inventory`,
  `messy`

---

## What Not to Do

- Do not use `argparse` — CLI is Typer only.
- Do not use `flask`, `fastapi`, or any web framework.
- Do not make network calls in generation (core, generators, renderers, CLI,
  API). The ONE sanctioned exception is the opt-in update check in
  `ui/app.py` (`check_update` / `_fetch_latest_release`): it runs only on an
  explicit "Check for Updates" click, reads the public GitHub Releases API,
  and sends no user data. Do not add any other network call, and do not make
  this one run automatically or at startup.
- Do not store or log user file paths.
- Do not add dependencies not in SPEC.md without flagging it.
- Do not use `WeasyPrint` — PDF renderer is `reportlab` only.
- Do not use `platypus.canvas` line-by-line for the PDF body — use
  `SimpleDocTemplate` + Flowables.
- Do not skip the watermark on any PDF page including page 2+.
- Do not use `float` for any currency value.

---

## Commit Style

- One logical change per commit.
- Message format: `type: short description`
  - `feat:` new capability
  - `fix:` bug fix
  - `refactor:` restructure without behavior change
  - `chore:` rename, move, cleanup
- Example: `feat: add PDF line-item table with computed totals`

---

## Phase A Exit Criteria

Phase A is complete when:

1. `pip install -e .` succeeds from repo root.
2. `recordforge generate --type invoice --format pdf --count 3` produces
   3 PDF files, each with a visible diagonal SAMPLE watermark, a header
   block, a line-item table, and a computed Total Due.
3. `recordforge generate --type customers --format xlsx --count 2`
   produces 2 XLSX files.
4. `from recordforge import generate; generate(type="invoice", format="pdf")`
   works in a Python REPL.
5. `python -m recordforge` launches the desktop UI with RecordForge
   branding.
6. `pytest tests/` passes.
7. Repo renamed to `recordforge`, README updated, v2.0.0 tagged.
