"""SQL INSERT renderer (Postgres / ANSI flavor).

Emits ``INSERT INTO`` statements only (no ``CREATE TABLE`` — column types are
the loader's choice). Identifiers are double-quoted so reserved words and mixed
case load cleanly; string literals double their single quotes per the SQL
standard. When rendering a bundle of related datasets, tables are written in the
order given, so a caller that passes them parents-first keeps foreign keys
resolvable on load. Output is deterministic (no timestamps) so a seeded run
reproduces byte for byte.
"""

import secrets
from decimal import Decimal
from pathlib import Path

from recordforge.core.faker_utils import sanitize_filename
from recordforge.core.models import GeneratedDoc

HEADER = (
    "-- RecordForge synthetic data (Postgres / ANSI SQL)\n"
    "-- FICTIONAL TEST DATA ONLY - generated for testing, demo, or training use.\n"
    "-- Tables are emitted parents-first so foreign keys resolve on load.\n"
)

# Rows per INSERT statement — keeps individual statements a sane size for large
# datasets and databases that cap statement length.
_BATCH = 500


def _ident(name: object) -> str:
    """Double-quote a table or column identifier (ANSI/Postgres safe)."""
    return '"' + str(name).replace('"', '""') + '"'


def _literal(value: object) -> str:
    """Render one Python value as a SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def _table_sql(table: str, rows: list[dict]) -> str:
    """Return the INSERT block for one table (batched into multi-row VALUES)."""
    if not rows:
        return f"-- {table}: no rows\n"

    columns = list(rows[0].keys())
    col_list = ", ".join(_ident(c) for c in columns)
    blocks: list[str] = []
    for start in range(0, len(rows), _BATCH):
        chunk = rows[start : start + _BATCH]
        value_rows = ",\n".join(
            "  (" + ", ".join(_literal(r.get(c)) for c in columns) + ")" for r in chunk
        )
        blocks.append(f"INSERT INTO {_ident(table)} ({col_list}) VALUES\n{value_rows};")
    return "\n".join(blocks) + "\n"


def render(dataset: str, rows: list[dict], output_dir: Path) -> GeneratedDoc:
    """Render a single table's rows to a .sql file."""
    stem = sanitize_filename(f"{dataset}_{secrets.token_hex(3)}")
    path = output_dir / f"{stem}.sql"
    path.write_text(HEADER + "\n" + _table_sql(dataset, rows), encoding="utf-8")
    return GeneratedDoc(path=path, doc_type=dataset, format="sql")


def render_bundle(
    datasets: dict[str, list[dict]], output_dir: Path, name: str = "bundle"
) -> GeneratedDoc:
    """Render several related tables into one .sql file, in the given order.

    The caller is responsible for passing ``datasets`` parents-first (both
    generate_related and generate_schema do) so the INSERTs load without
    violating foreign keys.
    """
    stem = sanitize_filename(f"{name}_{secrets.token_hex(3)}")
    path = output_dir / f"{stem}.sql"
    blocks = [HEADER]
    for table, rows in datasets.items():
        blocks.append(f"\n-- Table: {table} ({len(rows)} rows)")
        blocks.append(_table_sql(table, rows))
    path.write_text("\n".join(blocks), encoding="utf-8")
    return GeneratedDoc(path=path, doc_type=name, format="sql")
