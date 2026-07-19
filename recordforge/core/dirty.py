"""Post-generation dirtying transforms for data rows.

Takes clean rows and injects user-selected errors at controlled rates, so
teams can test data-cleaning and validation pipelines (and so learners can
practise cleanup drills). The user picks *which* errors to induce and at
*what* rate — dirt is a la carte, not a fixed schema.

All randomness flows through the passed ``rng``, so output is fully
reproducible under a seed. Cell-level transforms run in a fixed order
(independent of dict insertion order) and row-count-changing transforms
(duplicates) run last.
"""

import random
from decimal import Decimal
from typing import Callable

Rows = list[dict]

# Classic UTF-8-read-as-Latin-1 mojibake artifacts, keyed by base letter.
_MOJIBAKE = {
    "a": "Ã¡", "e": "Ã©", "i": "Ã­", "o": "Ã³", "u": "Ãº", "c": "Ã§", "n": "Ã±",
}


def _clamp(rate: float) -> float:
    return max(0.0, min(float(rate), 1.0))


def _is_number(v: object) -> bool:
    return isinstance(v, (int, float, Decimal)) and not isinstance(v, bool)


def _str_cells(row: dict) -> list[str]:
    return [k for k, v in row.items() if isinstance(v, str) and v]


def _num_cells(row: dict) -> list[str]:
    return [k for k, v in row.items() if _is_number(v)]


# --- individual transforms: fn(rows, rng, rate) -> rows ---

def _nulls(rows: Rows, rng: random.Random, rate: float) -> Rows:
    for row in rows:
        for k in list(row.keys()):
            if rng.random() < rate:
                row[k] = None
    return rows


def _blanks(rows: Rows, rng: random.Random, rate: float) -> Rows:
    for row in rows:
        for k in list(row.keys()):
            if rng.random() < rate:
                row[k] = ""
    return rows


def _whitespace(rows: Rows, rng: random.Random, rate: float) -> Rows:
    for row in rows:
        for k in _str_cells(row):
            if rng.random() < rate:
                pad = " " * rng.randint(1, 3)
                lead = pad if rng.random() < 0.5 else ""
                trail = pad if (lead == "" or rng.random() < 0.5) else ""
                row[k] = f"{lead}{row[k]}{trail}"
    return rows


def _case_drift(rows: Rows, rng: random.Random, rate: float) -> Rows:
    for row in rows:
        for k in _str_cells(row):
            if rng.random() < rate:
                val = row[k]
                row[k] = rng.choice([val.upper(), val.lower(), val.title(), val.swapcase()])
    return rows


def _format_drift(rows: Rows, rng: random.Random, rate: float) -> Rows:
    """Turn clean numeric cells into inconsistent string representations."""
    for row in rows:
        for k in _num_cells(row):
            if rng.random() < rate:
                v = row[k]
                variants = [f"${v}", f"{v} ", f"{v}.00", "N/A"]
                try:
                    variants.append(f"{int(v):,}")  # thousands separators
                except (ValueError, TypeError):
                    pass
                row[k] = rng.choice(variants)
    return rows


def _outliers(rows: Rows, rng: random.Random, rate: float) -> Rows:
    """Replace clean numeric cells with extreme / out-of-range values."""
    for row in rows:
        for k in _num_cells(row):
            if rng.random() < rate:
                v = row[k]
                factor = rng.choice([-1, 1000, 100000, 999999])
                row[k] = v * factor
    return rows


def _encoding(rows: Rows, rng: random.Random, rate: float) -> Rows:
    """Inject mojibake (encoding-corruption) artifacts into string cells."""
    for row in rows:
        for k in _str_cells(row):
            if rng.random() < rate:
                s = row[k]
                for i, ch in enumerate(s):
                    if ch.lower() in _MOJIBAKE:
                        row[k] = s[:i] + _MOJIBAKE[ch.lower()] + s[i + 1:]
                        break
    return rows


def _duplicates(rows: Rows, rng: random.Random, rate: float) -> Rows:
    """Append exact duplicate rows at the given per-row probability."""
    out: Rows = []
    for row in rows:
        out.append(row)
        if rng.random() < rate:
            out.append(dict(row))
    return out


DIRTY_TRANSFORMS: dict[str, Callable[[Rows, random.Random, float], Rows]] = {
    "nulls": _nulls,
    "blanks": _blanks,
    "whitespace": _whitespace,
    "case_drift": _case_drift,
    "format_drift": _format_drift,
    "outliers": _outliers,
    "encoding": _encoding,
    "duplicates": _duplicates,
}

# Cell-level transforms in fixed application order; duplicates applied last.
_CELL_ORDER = ("nulls", "blanks", "whitespace", "case_drift", "format_drift", "outliers", "encoding")

DIRTY_TYPES = tuple(DIRTY_TRANSFORMS.keys())


def apply_dirty(rows: Rows, rng: random.Random, config: dict[str, float]) -> Rows:
    """Apply the selected dirtying transforms to a copy of ``rows``.

    ``config`` maps error-type keys (see DIRTY_TYPES) to a rate in [0, 1].
    Cell-level rates are per-cell probabilities; ``duplicates`` is a per-row
    probability. Raises ValueError for an unknown error type.
    """
    for key in config:
        if key not in DIRTY_TRANSFORMS:
            valid = ", ".join(sorted(DIRTY_TRANSFORMS))
            raise ValueError(f"Unknown dirty error type '{key}'. Valid types: {valid}")

    result: Rows = [dict(r) for r in rows]

    for key in _CELL_ORDER:
        rate = _clamp(config.get(key, 0.0))
        if rate > 0:
            result = DIRTY_TRANSFORMS[key](result, rng, rate)

    dup_rate = _clamp(config.get("duplicates", 0.0))
    if dup_rate > 0:
        result = _duplicates(result, rng, dup_rate)

    return result
