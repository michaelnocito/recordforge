"""Load and validate a RecordForge schema from a YAML or JSON file.

Validation runs before any generation so errors point at the offending dataset
or column with a clear message, never a stack trace mid-write.
"""

import json as _json
from pathlib import Path

from recordforge.schema.columns import ALL_TYPES
from recordforge.schema.models import Column, Dataset, Schema


def _load_raw(path: Path) -> dict:
    """Parse the file into a plain dict, picking the parser by extension."""
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix in (".yml", ".yaml"):
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover - depends on install
            raise ValueError(
                "Reading YAML schemas needs pyyaml. Install it (pip install pyyaml) "
                "or use a .json schema file."
            ) from exc
        return yaml.safe_load(text)
    if suffix == ".json":
        return _json.loads(text)
    raise ValueError(
        f"Unsupported schema extension '{path.suffix}'. Use .yml, .yaml, or .json."
    )


def _parse_column(raw: object, ds_name: str) -> Column:
    if not isinstance(raw, dict):
        raise ValueError(f"Dataset '{ds_name}': each column must be a mapping, got {raw!r}.")
    name = raw.get("name")
    ctype = raw.get("type")
    if not name or not isinstance(name, str):
        raise ValueError(f"Dataset '{ds_name}': a column is missing a string 'name'.")
    if not ctype or not isinstance(ctype, str):
        raise ValueError(f"Dataset '{ds_name}', column '{name}': missing a 'type'.")
    if ctype not in ALL_TYPES:
        raise ValueError(
            f"Dataset '{ds_name}', column '{name}': unknown type '{ctype}'. "
            f"Valid types: {', '.join(sorted(ALL_TYPES))}."
        )
    params = {k: v for k, v in raw.items() if k not in ("name", "type")}
    return Column(name=name, type=ctype, params=params)


def _parse_dataset(raw: object) -> Dataset:
    if not isinstance(raw, dict):
        raise ValueError(f"Each dataset must be a mapping, got {raw!r}.")
    name = raw.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("A dataset is missing a string 'name'.")
    count = raw.get("count", 50)
    try:
        count = max(1, int(count))
    except (TypeError, ValueError):
        raise ValueError(f"Dataset '{name}': 'count' must be an integer.")
    raw_columns = raw.get("columns")
    if not isinstance(raw_columns, list) or not raw_columns:
        raise ValueError(f"Dataset '{name}': needs a non-empty 'columns' list.")
    columns = [_parse_column(c, name) for c in raw_columns]
    seen: set[str] = set()
    for col in columns:
        if col.name in seen:
            raise ValueError(f"Dataset '{name}': duplicate column '{col.name}'.")
        seen.add(col.name)
    return Dataset(name=name, count=count, columns=columns)


def _validate_relationships(schema: Schema) -> None:
    """Check every foreign key points at a real table.column."""
    tables = {ds.name: {c.name: c for c in ds.columns} for ds in schema.datasets}
    for ds in schema.datasets:
        for col in ds.columns:
            if col.type == "choice":
                values = col.params.get("values")
                if not isinstance(values, list) or not values:
                    raise ValueError(
                        f"Dataset '{ds.name}', column '{col.name}': "
                        "a 'choice' column needs a non-empty 'values' list."
                    )
            if col.type != "fk":
                continue
            ref = col.ref
            if not isinstance(ref, str) or ref.count(".") != 1:
                raise ValueError(
                    f"Dataset '{ds.name}', column '{col.name}': fk needs "
                    "ref: 'table.column'."
                )
            ref_table, ref_col = ref.split(".")
            if ref_table not in tables:
                raise ValueError(
                    f"Dataset '{ds.name}', column '{col.name}': fk references "
                    f"unknown table '{ref_table}'."
                )
            if ref_col not in tables[ref_table]:
                raise ValueError(
                    f"Dataset '{ds.name}', column '{col.name}': fk references "
                    f"unknown column '{ref_table}.{ref_col}'."
                )
            if ref_table == ds.name and tables[ref_table][ref_col].type != "id":
                raise ValueError(
                    f"Dataset '{ds.name}', column '{col.name}': a self-referencing "
                    "fk must point at an 'id' column in the same dataset."
                )


def load_schema(path: str | Path) -> Schema:
    """Load, parse, and validate a schema file. Raises ValueError on any problem."""
    path = Path(path)
    if not path.exists():
        raise ValueError(f"Schema file not found: {path}")

    raw = _load_raw(path)
    if not isinstance(raw, dict):
        raise ValueError("Schema root must be a mapping with a 'datasets' list.")

    raw_datasets = raw.get("datasets")
    if not isinstance(raw_datasets, list) or not raw_datasets:
        raise ValueError("Schema needs a non-empty 'datasets' list.")

    datasets = [_parse_dataset(d) for d in raw_datasets]
    names = [d.name for d in datasets]
    if len(names) != len(set(names)):
        raise ValueError("Schema has duplicate dataset names.")

    schema = Schema(name=str(raw.get("name") or path.stem), datasets=datasets)
    _validate_relationships(schema)
    return schema
