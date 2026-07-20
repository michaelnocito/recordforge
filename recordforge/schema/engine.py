"""Build datasets from a validated schema with referential integrity.

Tables are built in topological (parent-before-child) order so every foreign
key draws from a key pool that already exists. Self-referencing foreign keys
(for example ``manager_id -> employees.employee_id``) form a hierarchy pointed
at earlier rows, so they never create a cycle. A true cross-table cycle is
reported as an error, not silently mis-generated.
"""

import random

from recordforge.schema.columns import SCALAR_TYPES
from recordforge.schema.models import Column, Dataset, Schema


def topo_order(schema: Schema) -> list[str]:
    """Return dataset names in parent-before-child order (Kahn's algorithm).

    Edges run from a table to each other table its foreign keys depend on.
    Self-references are skipped (they are resolved within the table). Raises
    ValueError naming the tables involved if a cross-table cycle exists.
    """
    names = [ds.name for ds in schema.datasets]
    deps: dict[str, set[str]] = {name: set() for name in names}
    for ds in schema.datasets:
        for col in ds.columns:
            if col.type == "fk" and col.ref:
                ref_table = col.ref.split(".")[0]
                if ref_table != ds.name:
                    deps[ds.name].add(ref_table)

    order: list[str] = []
    resolved: set[str] = set()
    # Iterate in schema order among the currently-satisfiable tables so the
    # result is deterministic regardless of dict ordering.
    while len(order) < len(names):
        ready = [n for n in names if n not in resolved and deps[n] <= resolved]
        if not ready:
            blocked = sorted(n for n in names if n not in resolved)
            raise ValueError(
                "Schema has a circular foreign-key dependency among tables: "
                f"{', '.join(blocked)}. Break the cycle (a self-reference is fine, "
                "a table depending on another that depends back is not)."
            )
        for name in ready:
            order.append(name)
            resolved.add(name)
    return order


def _id_value(col: Column, index: int) -> str:
    """Deterministic sequential id: ``prefix`` + (start + index), optional width."""
    prefix = str(col.params.get("prefix", ""))
    start = int(col.params.get("start", 1))
    number = start + index
    width = col.params.get("width")
    if width:
        return f"{prefix}{number:0{int(width)}d}"
    return f"{prefix}{number}"


def _fk_value(
    rng: random.Random,
    col: Column,
    ds: Dataset,
    index: int,
    own_ids: dict[str, list[str]],
    pools: dict[str, dict[str, list]],
) -> object:
    """Resolve a foreign-key cell to a value that references a real parent key."""
    ref_table, ref_col = col.ref.split(".")
    if ref_table == ds.name:
        # Self-reference: row 0 is a null root, later rows point at an earlier
        # row, so the relationship is a tree with no cycle.
        pool = own_ids[ref_col]
        if index == 0:
            return None
        return rng.choice(pool[:index])
    return rng.choice(pools[ref_table][ref_col])


def _build_dataset(
    rng: random.Random, ds: Dataset, pools: dict[str, dict[str, list]]
) -> list[dict]:
    """Generate all rows for one dataset."""
    # Sequential ids are deterministic and consume no rng, so precompute them
    # up front — that lets a self-referencing fk see the id pool it points at.
    own_ids = {
        col.name: [_id_value(col, i) for i in range(ds.count)]
        for col in ds.columns
        if col.type == "id"
    }

    rows: list[dict] = []
    for i in range(ds.count):
        row: dict = {}
        for col in ds.columns:
            if col.type == "id":
                row[col.name] = own_ids[col.name][i]
            elif col.type == "fk":
                row[col.name] = _fk_value(rng, col, ds, i, own_ids, pools)
            else:
                row[col.name] = SCALAR_TYPES[col.type](rng, col)
        rows.append(row)
    return rows


def generate_datasets(rng: random.Random, schema: Schema) -> dict[str, list[dict]]:
    """Build every dataset with joinable foreign keys.

    Returns a dict keyed by dataset name in the schema's declared order (values
    are generated in topological order so parents exist before children).
    """
    order = topo_order(schema)
    pools: dict[str, dict[str, list]] = {}
    built: dict[str, list[dict]] = {}

    for name in order:
        ds = schema.dataset(name)
        rows = _build_dataset(rng, ds, pools)
        built[name] = rows
        pools[name] = {col.name: [r[col.name] for r in rows] for col in ds.columns}

    # Return in the schema's declared order for stable, predictable output.
    return {ds.name: built[ds.name] for ds in schema.datasets}
