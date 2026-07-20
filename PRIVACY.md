# Privacy & Data Safety

## What this app does

This app generates **entirely fictional** documents and data sets for testing, QA, demos, and training workflows. It does not collect, transmit, store, or log any personal information.

---

## What data is generated

All generated content — names, addresses, phone numbers, company names, dollar amounts, dates, and identifiers — is **randomly synthesized** at runtime using Python's `random` and `secrets` modules. No real people, companies, or transactions are represented.

---

## What data is NOT in this app

- No real names, addresses, or contact information
- No real company names or financial data
- No personal identifiers (SSNs, DOBs, account numbers)
- No real contracts, agreements, or legal documents
- No health, medical, or clinical records

---

## Network activity

All document and data generation runs **entirely offline**. Nothing you create, and no information about you or your machine, is ever sent anywhere. There is no telemetry, no analytics, and no account.

The app makes **exactly one** network request, and only when you click **Check for Updates**. It reads the project's public GitHub Releases page to compare the latest published version number against the one you are running, then tells you whether a newer version exists. That request sends no personal data and nothing about your files — only a standard request header naming the app and its version. If you never click the button, the app never touches the network. You can also just open the Releases page in your browser instead.

---

## Output files

Generated files are saved only to the folder you choose on your own machine. Nothing is uploaded or shared automatically.

---

## User-entered data

If you manually type a folder path, that path is used only to save files locally during that session. It is not stored, logged, or transmitted.

---

## Intended use

This tool is for:
- Software QA and testing
- OCR and document processing demos
- Data migration and cleanup workflow testing
- Training and onboarding demos

It is **not** for generating documents intended for legal, financial, medical, regulatory, identity, or any real-world use.

---

## Disclaimer

Every generated file includes an embedded disclaimer:

> FICTIONAL TEST DATA ONLY — generated for testing, demo, or training use.
