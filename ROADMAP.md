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

QA engineers, data and ETL engineers, developers, demo builders, trainers, and
teams testing OCR / document-AI / IDP pipelines who need realistic test material
without touching real customer data.

**RecordForge is not** an ML synthesizer that learns from your real data, a
live-database tool, a cloud service, or a single-invoice generator. It is a
lightweight, rule-based, offline forge.

---

## Shipping order

### Available now (v2.0.0)
- 6 document types (invoice, purchase order, contract, offer letter, intake
  form, SOP) as PDF / DOCX / HTML, every PDF watermarked.
- 6 data types (customers, vendors, transactions, employees, inventory, messy)
  as Excel.
- Desktop app, `pip` package, and CLI. Seedable for reproducible output.

### Next: data-forge upgrades
- **CSV / JSON / JSONL export** for all data types.
- **Control the number of rows** per file.
- **Choose the errors you want** — an a-la-carte "dirty data" menu: pick which
  problems to inject (nulls, duplicates, casing and format drift, whitespace,
  encoding corruption, orphan keys, out-of-range values) and at what rate, on any
  dataset. Great for practising data cleaning.
- **Edge-case corpus** — naughty strings, boundary values, unicode stress,
  injection payloads, extreme dates.
- **Checksum-valid identifiers** — valid-format card numbers and IBANs, plus
  safe non-routable test bank numbers.
- **Seed control in the desktop app.**

### Then: relational data (the big one)
- **Schema files** — define your own datasets, columns, types, and relationships
  in a small YAML/JSON file.
- **Referential integrity across datasets** — foreign keys that genuinely join
  across tables, generated from scratch, no database connection required.
- **Coherent records** — name, email, location, and phone that agree.
- **SQL INSERT and Parquet export**, in correct foreign-key order.

### Then: fits into your pipeline
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
