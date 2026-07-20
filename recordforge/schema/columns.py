"""Scalar column-type vocabulary for schema-driven generation.

Each generator takes ``(rng, column)`` and returns a single cell value. All
randomness flows through the passed rng — never a module global — so output is
reproducible under a seed. Foreign keys (``fk``) and sequential ids (``id``)
are NOT in this table: the engine handles them because they need the row index
and cross-table key pools.
"""

import random
import string as _string
from datetime import date, timedelta
from decimal import Decimal

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
from recordforge.schema.models import Column


def _int(rng: random.Random, col: Column) -> int:
    p = col.params
    return rng.randint(int(p.get("min", 0)), int(p.get("max", 1000)))


def _decimal(rng: random.Random, col: Column) -> Decimal:
    p = col.params
    lo, hi = float(p.get("min", 0)), float(p.get("max", 1000))
    places = int(p.get("places", 2))
    raw = lo + (hi - lo) * rng.random()
    return Decimal(str(raw)).quantize(Decimal(10) ** -places)


def _choice(rng: random.Random, col: Column) -> object:
    return rng.choice(col.params["values"])


def _date(rng: random.Random, col: Column) -> str:
    p = col.params
    back, forward = int(p.get("days_back", 365)), int(p.get("days_forward", 0))
    fmt = p.get("format", "%Y-%m-%d")
    return (date.today() + timedelta(days=rng.randint(-back, forward))).strftime(fmt)


def _bool(rng: random.Random, col: Column) -> bool:
    return rng.choice([True, False])


def _string(rng: random.Random, col: Column) -> str:
    length = int(col.params.get("length", 8))
    alphabet = _string.ascii_lowercase + _string.digits
    return "".join(rng.choice(alphabet) for _ in range(length))


# type key -> generator(rng, column) -> value
SCALAR_TYPES: dict[str, callable] = {
    "person": lambda rng, col: rand_person(rng),
    "full_name": lambda rng, col: rand_person(rng),
    "company": lambda rng, col: rand_company(rng),
    "email": lambda rng, col: rand_email(rng, rand_company(rng)),
    "phone": lambda rng, col: rand_phone(rng),
    "int": _int,
    "decimal": _decimal,
    "money": _decimal,
    "choice": _choice,
    "date": _date,
    "bool": _bool,
    "string": _string,
    "card": lambda rng, col: rand_card(rng)[1],
    "iban": lambda rng, col: rand_iban(rng),
    "routing_number": lambda rng, col: rand_routing_number(rng),
    "account_number": lambda rng, col: rand_account_number(rng),
}

# Types the engine handles directly rather than through SCALAR_TYPES.
SPECIAL_TYPES: tuple[str, ...] = ("id", "fk")

# Every valid column type key.
ALL_TYPES: tuple[str, ...] = tuple(SCALAR_TYPES) + SPECIAL_TYPES
