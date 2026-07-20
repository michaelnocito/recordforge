"""RecordForge — synthetic document and data file generator."""

from pathlib import Path

from recordforge.core.models import GeneratedDoc
from recordforge.core.seed import set_seed

__version__ = "2.1.0"


DATA_FORMATS = ("xlsx", "csv", "json", "jsonl", "sql", "parquet")
DOCUMENT_FORMATS = ("pdf", "docx", "html")

MAX_ROWS = 1_000_000


def _data_renderer_map() -> dict[str, callable]:
    """Per-dataset data renderers keyed by format (one file per dataset)."""
    from recordforge.renderers import (
        csv as csv_r, json as json_r, jsonl as jsonl_r,
        parquet as parquet_r, sql as sql_r, xlsx,
    )
    return {
        "xlsx": xlsx.render,
        "csv": csv_r.render,
        "json": json_r.render,
        "jsonl": jsonl_r.render,
        "sql": sql_r.render,
        "parquet": parquet_r.render,
    }


def generate(
    type: str,
    format: str,
    count: int = 1,
    output: str | Path | None = None,
    seed: int | None = None,
    rows: int = 50,
    dirty: dict[str, float] | None = None,
) -> list[GeneratedDoc]:
    """Generate synthetic documents or data files.

    ``count`` is the number of files. ``rows`` is the number of records per
    data file (ignored for document types). ``dirty`` optionally maps
    error-type keys to rates (see recordforge.core.dirty.DIRTY_TYPES) to
    inject controlled messiness into data rows. Returns a list of
    GeneratedDoc instances, one per file created. Raises ValueError for
    invalid type/format combinations.
    """
    from recordforge.core.dirty import apply_dirty
    from recordforge.core.seed import get_rng, set_seed as _set_seed
    from recordforge.generators.data import DATA_REGISTRY
    from recordforge.generators.documents import DOCUMENT_REGISTRY
    from recordforge.renderers import (
        csv as csv_r, docx, html, json as json_r, jsonl as jsonl_r,
        parquet as parquet_r, pdf, sql as sql_r, xlsx,
    )

    if seed is not None:
        _set_seed(seed)

    rng = get_rng()
    out_dir = Path(output) if output else Path.home() / "Documents" / "recordforge"
    out_dir.mkdir(parents=True, exist_ok=True)
    count = max(1, min(count, 100))
    rows = max(1, min(rows, MAX_ROWS))

    results: list[GeneratedDoc] = []

    if type in DOCUMENT_REGISTRY:
        if format not in DOCUMENT_FORMATS:
            raise ValueError(
                f"Format '{format}' is not valid for document types. Use pdf, docx, or html."
            )
        _doc_renderers = {"pdf": pdf.render, "docx": docx.render, "html": html.render}
        builder = DOCUMENT_REGISTRY[type]
        renderer = _doc_renderers[format]
        for _ in range(count):
            results.append(renderer(builder(rng), out_dir))

    elif type in DATA_REGISTRY:
        if format not in DATA_FORMATS:
            raise ValueError(
                f"Format '{format}' is not valid for data types. "
                f"Use {', '.join(DATA_FORMATS)}."
            )
        _data_renderers = {
            "xlsx": xlsx.render,
            "csv": csv_r.render,
            "json": json_r.render,
            "jsonl": jsonl_r.render,
            "sql": sql_r.render,
            "parquet": parquet_r.render,
        }
        builder = DATA_REGISTRY[type]
        renderer = _data_renderers[format]
        for _ in range(count):
            data_rows = builder(rng, rows)
            if dirty:
                data_rows = apply_dirty(data_rows, rng, dirty)
            results.append(renderer(type, data_rows, out_dir))

    else:
        valid = sorted(DOCUMENT_REGISTRY) + sorted(DATA_REGISTRY)
        raise ValueError(f"Unknown type '{type}'. Valid types: {', '.join(valid)}")

    return results


def generate_related(
    output: str | Path | None = None,
    format: str = "csv",
    seed: int | None = None,
    customers: int = 100,
    transactions: int = 500,
    payments: int = 200,
) -> list[GeneratedDoc]:
    """Generate a relational bundle: customers, transactions, and payments with
    real foreign keys, rendered to one data ``format`` each.

    ``transactions.customer_id`` is always drawn from the generated
    ``customers.customer_id`` pool, and every payment settles a real
    transaction, so the output joins with no orphan keys. Files are written in
    dependency order (customers, then transactions, then payments); the ``sql``
    format instead writes a single FK-ordered .sql file. Returns a list of
    GeneratedDoc instances. Raises ValueError for an invalid data format.
    """
    from recordforge.core.seed import get_rng, set_seed as _set_seed
    from recordforge.generators.related import RELATED_DATASETS, build_related

    if format not in DATA_FORMATS:
        raise ValueError(
            f"Format '{format}' is not valid for relational bundles. "
            f"Use {', '.join(DATA_FORMATS)}."
        )

    if seed is not None:
        _set_seed(seed)

    rng = get_rng()
    out_dir = Path(output) if output else Path.home() / "Documents" / "recordforge"
    out_dir.mkdir(parents=True, exist_ok=True)

    spec = {
        "customers": max(1, min(customers, MAX_ROWS)),
        "transactions": max(1, min(transactions, MAX_ROWS)),
        "payments": max(1, min(payments, MAX_ROWS)),
    }
    datasets = build_related(rng, spec)
    ordered = {name: datasets[name] for name in RELATED_DATASETS}

    if format == "sql":
        from recordforge.renderers import sql as sql_r
        return [sql_r.render_bundle(ordered, out_dir, name="related")]

    renderer = _data_renderer_map()[format]
    return [renderer(name, rows, out_dir) for name, rows in ordered.items()]


def generate_schema(
    schema_path: str | Path,
    output: str | Path | None = None,
    format: str = "csv",
    seed: int | None = None,
) -> list[GeneratedDoc]:
    """Generate a set of linked datasets from a YAML or JSON schema file.

    The schema declares datasets, their columns (from a supported type
    vocabulary), and foreign-key relationships. Datasets are generated in
    dependency order so every foreign key resolves to a real parent key, then
    each is rendered to one data ``format``. The ``sql`` format instead writes a
    single .sql file with all tables in FK-safe (topological) order. Returns a
    list of GeneratedDoc instances. Raises ValueError for an invalid format or
    an invalid schema.
    """
    from recordforge.core.seed import get_rng, set_seed as _set_seed
    from recordforge.schema import generate_datasets, load_schema

    if format not in DATA_FORMATS:
        raise ValueError(
            f"Format '{format}' is not valid for schemas. "
            f"Use {', '.join(DATA_FORMATS)}."
        )

    schema = load_schema(schema_path)

    if seed is not None:
        _set_seed(seed)

    rng = get_rng()
    out_dir = Path(output) if output else Path.home() / "Documents" / "recordforge"
    out_dir.mkdir(parents=True, exist_ok=True)

    datasets = generate_datasets(rng, schema)

    if format == "sql":
        from recordforge.renderers import sql as sql_r
        from recordforge.schema import topo_order
        ordered = {name: datasets[name] for name in topo_order(schema)}
        return [sql_r.render_bundle(ordered, out_dir, name=schema.name)]

    renderer = _data_renderer_map()[format]
    return [renderer(name, rows, out_dir) for name, rows in datasets.items()]


def list_types() -> dict[str, list[str]]:
    """Return all available type keys grouped by category."""
    from recordforge.generators.data import DATA_REGISTRY
    from recordforge.generators.documents import DOCUMENT_REGISTRY

    return {
        "documents": sorted(DOCUMENT_REGISTRY.keys()),
        "data": sorted(DATA_REGISTRY.keys()),
    }


__all__ = [
    "generate",
    "generate_related",
    "generate_schema",
    "list_types",
    "set_seed",
    "GeneratedDoc",
    "__version__",
]
