"""Phase A smoke tests."""

import random
from decimal import Decimal
from pathlib import Path

import pytest

from recordforge.core.models import DocumentData, GeneratedDoc
from recordforge.core.seed import get_rng, set_seed


# --- Generator smoke tests ---

def _fresh_rng() -> random.Random:
    return random.Random(12345)


def test_invoice_build():
    from recordforge.generators.documents.invoice import build
    data = build(_fresh_rng())
    assert isinstance(data, DocumentData)
    assert data.doc_type == "invoice"
    assert data.doc_number.startswith("INV-")
    assert 2 <= len(data.line_items) <= 4


def test_purchase_order_build():
    from recordforge.generators.documents.purchase_order import build
    data = build(_fresh_rng())
    assert data.doc_type == "purchase_order"
    assert data.doc_number.startswith("PO-")
    assert 3 <= len(data.line_items) <= 6


def test_intake_form_build():
    from recordforge.generators.documents.intake_form import build
    data = build(_fresh_rng())
    assert data.doc_type == "intake_form"
    assert len(data.line_items) == 0
    assert data.notes


def test_sop_build():
    from recordforge.generators.documents.sop import build
    data = build(_fresh_rng())
    assert data.doc_type == "sop"
    assert len(data.line_items) == 0


def test_contract_build():
    from recordforge.generators.documents.contract import build
    data = build(_fresh_rng())
    assert data.doc_type == "contract"
    assert len(data.line_items) == 0
    assert "SERVICES AGREEMENT" in data.notes


def test_offer_letter_build():
    from recordforge.generators.documents.offer_letter import build
    data = build(_fresh_rng())
    assert data.doc_type == "offer_letter"
    assert len(data.line_items) == 0
    assert "Base Salary" in data.notes


# --- Line item math ---

def test_line_item_totals_are_computed():
    from recordforge.generators.documents.invoice import build
    data = build(_fresh_rng())
    for item in data.line_items:
        assert item.total == Decimal(item.quantity) * item.unit_price
    assert data.subtotal == sum(i.total for i in data.line_items)
    assert data.total_due == data.subtotal + data.tax


# --- Date ordering ---

def test_invoice_due_date_after_doc_date():
    from datetime import datetime
    from recordforge.generators.documents.invoice import build
    data = build(_fresh_rng())
    fmt = "%B %d, %Y"
    doc = datetime.strptime(data.doc_date, fmt)
    due = datetime.strptime(data.due_date, fmt)
    assert due > doc


# --- Data generator smoke tests ---

def test_customers_build_rows():
    from recordforge.generators.data.customers import build_rows
    rows = build_rows(_fresh_rng(), count=10)
    assert len(rows) == 10
    assert "customer_id" in rows[0]
    assert rows[0]["customer_id"] == "CUST-1000"


def test_vendors_build_rows():
    from recordforge.generators.data.vendors import build_rows
    rows = build_rows(_fresh_rng(), count=5)
    assert len(rows) == 5
    assert "vendor_id" in rows[0]


def test_transactions_build_rows():
    from recordforge.generators.data.transactions import build_rows
    rows = build_rows(_fresh_rng(), count=5)
    assert all(r["currency"] == "USD" for r in rows)


def test_employees_build_rows():
    from recordforge.generators.data.employees import build_rows
    rows = build_rows(_fresh_rng(), count=5)
    assert "employee_id" in rows[0]


def test_inventory_build_rows():
    from recordforge.generators.data.inventory import build_rows
    rows = build_rows(_fresh_rng(), count=5)
    assert "sku" in rows[0]


def test_messy_build_rows():
    from recordforge.generators.data.messy import build_rows
    rows = build_rows(_fresh_rng(), count=20)
    # Must contain at least some None values (dirty by design)
    all_values = [v for row in rows for v in row.values()]
    assert None in all_values


# --- Renderer smoke tests ---

def test_pdf_renderer_produces_nonempty_file(tmp_path: Path):
    from recordforge.generators.documents.invoice import build
    from recordforge.renderers.pdf import render
    data = build(_fresh_rng())
    doc = render(data, tmp_path)
    assert isinstance(doc, GeneratedDoc)
    assert doc.path.exists()
    assert doc.path.stat().st_size > 0


def test_docx_renderer_produces_nonempty_file(tmp_path: Path):
    from recordforge.generators.documents.invoice import build
    from recordforge.renderers.docx import render
    data = build(_fresh_rng())
    doc = render(data, tmp_path)
    assert doc.path.exists()
    assert doc.path.stat().st_size > 0


def test_html_renderer_produces_nonempty_file(tmp_path: Path):
    from recordforge.generators.documents.invoice import build
    from recordforge.renderers.html import render
    data = build(_fresh_rng())
    doc = render(data, tmp_path)
    assert doc.path.exists()
    content = doc.path.read_text(encoding="utf-8")
    assert "SAMPLE" in content
    assert data.doc_number in content


def test_xlsx_renderer_produces_nonempty_file(tmp_path: Path):
    from recordforge.generators.data.customers import build_rows
    from recordforge.renderers.xlsx import render
    rows = build_rows(_fresh_rng(), count=10)
    doc = render("customers", rows, tmp_path)
    assert doc.path.exists()
    assert doc.path.stat().st_size > 0


# --- Watermark test ---

def test_pdf_contains_sample_watermark(tmp_path: Path):
    """Generated PDF contains watermark indicators: Helvetica-Bold font and 0.15 alpha."""
    from recordforge.generators.documents.invoice import build
    from recordforge.renderers.pdf import render
    data = build(_fresh_rng())
    doc = render(data, tmp_path)
    raw = doc.path.read_bytes()
    # Watermark uses Helvetica-Bold at alpha 0.15 — both appear uncompressed in PDF metadata
    assert b"Helvetica-Bold" in raw
    assert b"/ca .15" in raw


# --- Data renderers: csv / json / jsonl ---

def test_csv_renderer_roundtrips(tmp_path: Path):
    import csv as _csv
    from recordforge.generators.data.customers import build_rows
    from recordforge.renderers.csv import render
    rows = build_rows(_fresh_rng(), count=8)
    doc = render("customers", rows, tmp_path)
    assert doc.format == "csv" and doc.path.suffix == ".csv"
    read = list(_csv.DictReader(doc.path.open(encoding="utf-8")))
    assert len(read) == 8
    assert read[0]["customer_id"] == "CUST-1000"


def test_json_renderer_is_valid_array(tmp_path: Path):
    import json as _json
    from recordforge.generators.data.customers import build_rows
    from recordforge.renderers.json import render
    rows = build_rows(_fresh_rng(), count=6)
    doc = render("customers", rows, tmp_path)
    data = _json.loads(doc.path.read_text(encoding="utf-8"))
    assert isinstance(data, list) and len(data) == 6


def test_jsonl_renderer_one_object_per_line(tmp_path: Path):
    import json as _json
    from recordforge.generators.data.customers import build_rows
    from recordforge.renderers.jsonl import render
    rows = build_rows(_fresh_rng(), count=7)
    doc = render("customers", rows, tmp_path)
    lines = [ln for ln in doc.path.read_text(encoding="utf-8").splitlines() if ln]
    assert len(lines) == 7
    assert all(isinstance(_json.loads(ln), dict) for ln in lines)


def test_messy_none_serializes_in_csv_and_json(tmp_path: Path):
    import json as _json
    from recordforge.generators.data.messy import build_rows
    from recordforge.renderers.csv import render as render_csv
    from recordforge.renderers.json import render as render_json
    rows = build_rows(_fresh_rng(), count=10)
    csv_doc = render_csv("messy", rows, tmp_path)
    json_doc = render_json("messy", rows, tmp_path)
    assert csv_doc.path.stat().st_size > 0
    assert len(_json.loads(json_doc.path.read_text(encoding="utf-8"))) == 10


# --- API: rows control and format validation ---

def test_generate_rows_controls_row_count(tmp_path: Path):
    import json as _json
    import recordforge as rf
    doc = rf.generate(type="customers", format="json", count=1, output=tmp_path, rows=17)[0]
    assert len(_json.loads(doc.path.read_text(encoding="utf-8"))) == 17


def test_generate_rejects_bad_data_format(tmp_path: Path):
    import recordforge as rf
    with pytest.raises(ValueError):
        rf.generate(type="customers", format="pdf", output=tmp_path)


def test_generate_rejects_data_format_on_documents(tmp_path: Path):
    import recordforge as rf
    with pytest.raises(ValueError):
        rf.generate(type="invoice", format="csv", output=tmp_path)


def test_generate_data_formats_are_reproducible(tmp_path: Path):
    import recordforge as rf
    a = rf.generate(type="customers", format="jsonl", output=tmp_path, seed=5, rows=12)[0]
    b = rf.generate(type="customers", format="jsonl", output=tmp_path, seed=5, rows=12)[0]
    assert a.path.read_text(encoding="utf-8") == b.path.read_text(encoding="utf-8")


# --- Desktop bridge seed ---

def test_ui_bridge_seed_is_reproducible(tmp_path: Path):
    from recordforge.ui.app import API

    def run(out):
        return API().generate({
            "mode": "data", "docTypes": ["customers", "payments"], "quantity": 2,
            "dataFormat": "csv", "rows": 6, "seed": 1234, "outputFolder": str(out),
        })

    a, b = run(tmp_path / "a"), run(tmp_path / "b")
    assert a["success"] and b["success"]

    def by_type(files):
        out = {}
        for f in files:
            out.setdefault(Path(f).name.split("_")[0], []).append(Path(f).read_text(encoding="utf-8"))
        return out

    ta, tb = by_type(a["files"]), by_type(b["files"])
    # same seed -> same content per type across runs
    assert sorted(ta) == sorted(tb)
    for key in ta:
        assert sorted(ta[key]) == sorted(tb[key])
    # two files of one type still differ (rng advances within a batch)
    assert ta["customers"][0] != ta["customers"][1]


# --- Checksum-valid identifiers ---

def _luhn_ok(number: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(number)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _iban_ok(iban: str) -> bool:
    rearranged = iban[4:] + iban[:4]
    numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    return int(numeric) % 97 == 1


def _aba_ok(n: str) -> bool:
    d = [int(x) for x in n]
    return (3 * (d[0] + d[3] + d[6]) + 7 * (d[1] + d[4] + d[7]) + (d[2] + d[5] + d[8])) % 10 == 0


def test_card_numbers_are_luhn_valid():
    from recordforge.core.faker_utils import rand_card
    rng = random.Random(3)
    cards = [rand_card(rng) for _ in range(200)]
    assert all(_luhn_ok(num) for _, num in cards)
    assert all(len(num) in (15, 16) for _, num in cards)


def test_ibans_are_mod97_valid():
    from recordforge.core.faker_utils import rand_iban
    rng = random.Random(3)
    assert all(_iban_ok(rand_iban(rng)) for _ in range(200))


def test_routing_numbers_valid_but_non_routable():
    from recordforge.core.faker_utils import rand_routing_number
    rng = random.Random(3)
    for _ in range(200):
        n = rand_routing_number(rng)
        assert len(n) == 9 and _aba_ok(n)
        assert n.startswith("99")  # unassigned Fed prefix -> non-routable


def test_payments_type_registered(tmp_path: Path):
    import recordforge as rf
    assert "payments" in rf.list_types()["data"]
    doc = rf.generate(type="payments", format="csv", rows=10, output=tmp_path)[0]
    assert doc.path.exists() and doc.path.stat().st_size > 0


# --- Edge-case corpus ---

def test_edge_cases_build_rows():
    from recordforge.generators.data.edge_cases import build_rows
    rows = build_rows(_fresh_rng(), count=60)
    assert len(rows) == 60
    assert {"edge_id", "category", "label", "value"} == set(rows[0].keys())
    # small count still spans several categories thanks to interleaving
    assert len({r["category"] for r in build_rows(_fresh_rng(), count=8)}) >= 5


def test_edge_cases_registered_and_json_valid(tmp_path: Path):
    import json as _json
    import recordforge as rf
    assert "edge_cases" in rf.list_types()["data"]
    doc = rf.generate(type="edge_cases", format="json", rows=200, output=tmp_path)[0]
    data = _json.loads(doc.path.read_text(encoding="utf-8"))  # must be valid JSON (no NaN/Infinity)
    assert len({r["category"] for r in data}) >= 8


def test_edge_cases_are_stable():
    from recordforge.generators.data.edge_cases import build_rows
    assert build_rows(random.Random(1), 30) == build_rows(random.Random(999), 30)


# --- Dirtying engine ---

def _clean_rows(n=20):
    return [{"id": i, "name": f"Name{i}", "amount": 100 + i} for i in range(n)]


def test_dirty_nulls_injects_none():
    from recordforge.core.dirty import apply_dirty
    out = apply_dirty(_clean_rows(), _fresh_rng(), {"nulls": 0.5})
    assert any(v is None for row in out for v in row.values())


def test_dirty_duplicates_grows_row_count():
    from recordforge.core.dirty import apply_dirty
    out = apply_dirty(_clean_rows(20), _fresh_rng(), {"duplicates": 1.0})
    assert len(out) == 40  # every row duplicated once at rate 1.0


def test_dirty_does_not_mutate_input():
    from recordforge.core.dirty import apply_dirty
    clean = _clean_rows(10)
    apply_dirty(clean, _fresh_rng(), {"nulls": 1.0})
    assert all(row["id"] is not None for row in clean)  # original untouched


def test_dirty_is_deterministic_under_seed():
    from recordforge.core.dirty import apply_dirty
    cfg = {"nulls": 0.2, "case_drift": 0.3, "encoding": 0.2, "duplicates": 0.1}
    a = apply_dirty(_clean_rows(), random.Random(9), cfg)
    b = apply_dirty(_clean_rows(), random.Random(9), cfg)
    assert a == b


def test_dirty_rejects_unknown_type():
    from recordforge.core.dirty import apply_dirty
    with pytest.raises(ValueError):
        apply_dirty(_clean_rows(), _fresh_rng(), {"bogus": 0.1})


def test_generate_applies_dirty(tmp_path: Path):
    import csv as _csv
    import recordforge as rf
    doc = rf.generate(
        type="customers", format="csv", rows=40, seed=3, output=tmp_path,
        dirty={"nulls": 0.3, "duplicates": 0.2},
    )[0]
    read = list(_csv.DictReader(doc.path.open(encoding="utf-8")))
    assert len(read) > 40  # duplicates added rows
    assert any(v == "" for row in read for v in row.values())  # nulls -> empty in CSV


def test_cli_parse_dirty():
    from recordforge.cli import _parse_dirty
    assert _parse_dirty("nulls=0.1, case_drift=0.2 ,duplicates=0.05") == {
        "nulls": 0.1, "case_drift": 0.2, "duplicates": 0.05,
    }
    with pytest.raises(ValueError):
        _parse_dirty("nulls")


# --- Seed reproducibility ---

def test_same_seed_same_doc_number():
    from recordforge.generators.documents.invoice import build
    set_seed(99)
    a = build(get_rng())
    set_seed(99)
    b = build(get_rng())
    assert a.doc_number == b.doc_number


def test_same_seed_same_total_due():
    from recordforge.generators.documents.invoice import build
    set_seed(42)
    a = build(get_rng())
    set_seed(42)
    b = build(get_rng())
    assert a.total_due == b.total_due
