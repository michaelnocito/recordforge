"""Payments dataset generator.

Rows carry checksum-valid but fake financial identifiers: Luhn-valid card
numbers (test BIN ranges), mod-97-valid IBANs, and ABA-checksum-valid but
non-routable routing numbers. They pass format validators in a test pipeline
while never being real accounts.
"""

import random

from recordforge.core.faker_utils import (
    rand_account_number,
    rand_card,
    rand_iban,
    rand_person,
    rand_routing_number,
)


def build_rows(rng: random.Random, count: int = 50) -> list[dict]:
    """Build a list of randomized payment row dicts.

    Schema: payment_id, account_holder, card_brand, card_number, iban,
            routing_number, account_number, amount, currency
    """
    rows = []
    for i in range(count):
        brand, card_number = rand_card(rng)
        rows.append({
            "payment_id": f"PAY-{100000 + i}",
            "account_holder": rand_person(rng),
            "card_brand": brand,
            "card_number": card_number,
            "iban": rand_iban(rng),
            "routing_number": rand_routing_number(rng),
            "account_number": rand_account_number(rng),
            "amount": rng.randint(10, 25000),
            "currency": rng.choice(["USD", "EUR", "GBP"]),
        })
    return rows
