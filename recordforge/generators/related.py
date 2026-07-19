"""Relational bundle generator — linked datasets with real foreign keys.

Generates customers, transactions, and payments in one pass so foreign keys
actually join. Every ``transactions.customer_id`` is drawn from the generated
``customers.customer_id`` pool, and every payment settles a real transaction,
inheriting its ``txn_id`` and ``customer_id``. This is referential integrity by
construction: parents are built before children, children only reference keys
that exist, so the output never contains an orphan foreign key.

Deterministic under a seeded rng and offline like every other generator.
"""

import random
from datetime import date, timedelta

from recordforge.core.faker_utils import (
    rand_account_number,
    rand_card,
    rand_company,
    rand_email,
    rand_iban,
    rand_person,
    rand_phone,
    rand_routing_number,
)

# Datasets in dependency (parent-before-child) order. Renderers and inserts
# should follow this order so foreign keys resolve.
RELATED_DATASETS: tuple[str, ...] = ("customers", "transactions", "payments")

DEFAULT_COUNTS: dict[str, int] = {"customers": 100, "transactions": 500, "payments": 200}


def _build_customers(rng: random.Random, count: int) -> list[dict]:
    """Build the parent customer rows. Schema matches the standalone type."""
    rows: list[dict] = []
    for i in range(count):
        company = rand_company(rng)
        rows.append({
            "customer_id": f"CUST-{1000 + i}",
            "name": rand_person(rng),
            "company": company,
            "email": rand_email(rng, company),
            "phone": rand_phone(rng),
        })
    return rows


def _build_transactions(rng: random.Random, count: int, customers: list[dict]) -> list[dict]:
    """Build transactions, each referencing a real customer_id."""
    customer_ids = [c["customer_id"] for c in customers]
    rows: list[dict] = []
    for i in range(count):
        posted = date.today() + timedelta(days=rng.randint(-180, 0))
        rows.append({
            "txn_id": f"TXN-{100000 + i}",
            "customer_id": rng.choice(customer_ids),
            "account": f"ACCT-{rng.randint(1000, 9999)}",
            "amount": rng.randint(50, 5000),
            "currency": "USD",
            "posted_date": posted.strftime("%Y-%m-%d"),
        })
    return rows


def _build_payments(
    rng: random.Random, count: int, customers: list[dict], transactions: list[dict]
) -> list[dict]:
    """Build payments that settle real transactions.

    Each payment inherits the transaction's txn_id, customer_id, amount, and
    currency, and names the matching customer as account_holder — so the whole
    customer -> transaction -> payment chain stays internally consistent.
    """
    customer_by_id = {c["customer_id"]: c for c in customers}
    rows: list[dict] = []
    for i in range(count):
        txn = rng.choice(transactions)
        customer = customer_by_id[txn["customer_id"]]
        brand, card_number = rand_card(rng)
        rows.append({
            "payment_id": f"PAY-{100000 + i}",
            "customer_id": txn["customer_id"],
            "txn_id": txn["txn_id"],
            "account_holder": customer["name"],
            "card_brand": brand,
            "card_number": card_number,
            "iban": rand_iban(rng),
            "routing_number": rand_routing_number(rng),
            "account_number": rand_account_number(rng),
            "amount": txn["amount"],
            "currency": txn["currency"],
        })
    return rows


def build_related(rng: random.Random, spec: dict[str, int] | None = None) -> dict[str, list[dict]]:
    """Build customers, transactions, and payments with joinable foreign keys.

    ``spec`` maps dataset name to row count; any missing or unknown keys fall
    back to DEFAULT_COUNTS. Datasets are generated in dependency order so every
    child key references a real parent. Returns a dict keyed by dataset name.
    """
    counts = dict(DEFAULT_COUNTS)
    if spec:
        counts.update({k: v for k, v in spec.items() if k in DEFAULT_COUNTS})
    counts = {k: max(1, int(v)) for k, v in counts.items()}

    customers = _build_customers(rng, counts["customers"])
    transactions = _build_transactions(rng, counts["transactions"], customers)
    payments = _build_payments(rng, counts["payments"], customers, transactions)
    return {"customers": customers, "transactions": transactions, "payments": payments}
