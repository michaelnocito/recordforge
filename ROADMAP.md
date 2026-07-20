# RecordForge Roadmap

RecordForge generates realistic, clearly-synthetic test **data** and
**documents** on your machine. No cloud, no upload, no account, no row caps.
Use the desktop app, the `pip` package, or the CLI, all over one engine.

RecordForge is, and will stay, **free and open source.**

---

## What guides the roadmap

Five pillars. If a feature serves none of them, it does not ship.

1. **Trustworthy by construction** — nothing leaves your machine. No network
   calls, no telemetry, works air-gapped. Every document is unmistakably
   synthetic: visible watermark, deliberately fictitious and non-routable
   identifiers, and provenance metadata in the file.
2. **Coherent & relational** — data that works together: foreign keys that
   actually join, fields that agree within a record, checksums that validate,
   money math that computes.
3. **Deterministic & reproducible** — same seed, same output. Schema and seed
   are small text files you can commit to a repo and regenerate identically.
4. **One engine, two surfaces, many formats** — a polished desktop app for
   one-offs and a `pip` library + CLI for automation, exporting the formats
   teams actually use.
5. **Realism with a purpose** — not just clean data, but controlled messiness,
   edge cases, and (for documents) ground-truth labels for testing OCR and
   document-AI pipelines.

---

## Who it is for

Anyone who builds, tests, teaches, or analyzes with data and documents but
cannot use real customer records. The roles we design and validate against:

- **Data engineers / ETL developers** — need linked tables with real foreign
  keys, SQL and Parquet output, and schema files they can commit and regenerate.
- **Data migration analysts** — need believable source data (and deliberately
  broken data) to rehearse and validate a migration before touching production.
- **Data analysts and junior data analysts** — need practice datasets to write
  queries, build models, and learn cleaning without a live warehouse.
- **Business analysts** — need realistic sample records and documents to mock up
  reports, requirements, and process flows.
- **Financial analysts** — need transactions, payments, and invoices with money
  math and valid-format (but fake) identifiers.
- **QA and test engineers** — need edge cases, messy data, and integrity breakers
  to harden parsers, validators, and pipelines.
- **Trainers, course builders, and demo teams** — need repeatable, shareable
  datasets and documents for teaching and presentations.

**RecordForge is not** an ML synthesizer that learns from your real data, a
live-database tool, a cloud service, or a single-invoice generator. It is a
lightweight, rule-based, offline forge.

Each release is validated against these roles with a task-based walkthrough
(what each role actually comes to the tool to do). The detailed checklist lives
outside the public repo.

---

## Shipping order

### Shipped

**Base (v2.0.0)**
- 6 document types (invoice, purchase order, contract, offer letter, intake
  form, SOP) as PDF / DOCX / HTML, every PDF watermarked.
- Desktop app, `pip` package, and CLI. Seedable for reproducible output.

**Data-forge upgrades (v2.1.0)**
- **CSV / JSON / JSONL export** for all data types, with row-count control.
- **A-la-carte "dirty data" menu** — pick which problems to inject (nulls,
  blanks, whitespace, casing and format drift, encoding corruption, outliers,
  duplicates) and at what rate, on any dataset.
- **Edge-case corpus** — naughty strings, boundary values, unicode stress,
  injection payloads, extreme dates.
- **Checksum-valid identifiers** and a `payments` data type — valid-format card
  numbers and IBANs, plus safe non-routable test bank numbers.
- **Seed control in the desktop app.**

**Relational data — the big one (v2.1.0)**
- **Built-in relational bundle** — customers, transactions, and payments
  generated together with real, joinable foreign keys.
- **Schema files** — define your own datasets, columns, types, and relationships
  in a small YAML or JSON file; RecordForge resolves build order, key pools, and
  self-references, and rejects circular dependencies with a clear error.
- **Referential integrity across datasets** — foreign keys that genuinely join,
  generated from scratch, no database connection required.
- **SQL INSERT and Parquet export**, with SQL written in correct
  foreign-key order so it loads cleanly.

### Next: fits into your pipeline
- **pytest plugin, dbt-seed output, and CI recipes.**
- **Integrity breakers** — deliberately invalid data (orphan keys, ragged rows,
  encoding corruption) to test your validation and constraints.

### Then: document differentiation
- **More document types** with full guardrails: bank statement, pay stub,
  remittance advice, delivery note, and tax forms (W-2 / 1099). Every one
  watermarked, with fictitious non-routable identifiers and provenance metadata.
- **Ground-truth labels** shipped beside each document, so you can auto-score an
  OCR or extraction pipeline.
- **Provenance metadata** backing the visible watermark.

### Later, if the need is there
- Deep healthcare realism (standard code sets, FHIR).
- macOS / Linux desktop builds.
- Locale / internationalization.

---

*Have a use case that isn't covered? Open an issue.*
