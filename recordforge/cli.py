"""Typer CLI for RecordForge."""

from pathlib import Path
from typing import Optional

import typer

from recordforge import __version__

app = typer.Typer(name="recordforge", help="Generate synthetic documents and data files.")


def _parse_dirty(spec: str) -> dict[str, float]:
    """Parse a --dirty spec like 'nulls=0.1,case_drift=0.2' into a dict."""
    config: dict[str, float] = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise ValueError(f"Invalid --dirty item '{part}'. Use key=rate, e.g. nulls=0.1")
        key, _, rate = part.partition("=")
        try:
            config[key.strip()] = float(rate.strip())
        except ValueError:
            raise ValueError(f"Invalid rate in '{part}'. Rate must be a number, e.g. nulls=0.1")
    return config


@app.command()
def generate(
    type: str = typer.Option(..., "--type", help="Document or data type key"),
    format: str = typer.Option(
        ..., "--format", help="Documents: pdf | docx | html.  Data: xlsx | csv | json | jsonl"
    ),
    count: int = typer.Option(1, "--count", help="Number of files to generate (1–100)"),
    rows: int = typer.Option(50, "--rows", help="Rows per data file (ignored for documents)"),
    dirty: Optional[str] = typer.Option(
        None,
        "--dirty",
        help="Inject errors into data, e.g. 'nulls=0.1,case_drift=0.2,duplicates=0.05'",
    ),
    output: Optional[Path] = typer.Option(None, "--output", help="Output directory"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Integer seed for reproducible output"),
) -> None:
    """Generate synthetic documents or data files."""
    import recordforge as rf

    try:
        dirty_config = _parse_dirty(dirty) if dirty else None
        docs = rf.generate(
            type=type, format=format, count=count, output=output, seed=seed,
            rows=rows, dirty=dirty_config,
        )
        for doc in docs:
            typer.echo(str(doc.path))
        typer.echo(f"\nGenerated {len(docs)} file(s).")
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


@app.command(name="generate-related")
def generate_related(
    format: str = typer.Option("csv", "--format", help="Data format: xlsx | csv | json | jsonl"),
    customers: int = typer.Option(100, "--customers", help="Number of customer rows"),
    transactions: int = typer.Option(500, "--transactions", help="Number of transaction rows"),
    payments: int = typer.Option(200, "--payments", help="Number of payment rows"),
    output: Optional[Path] = typer.Option(None, "--output", help="Output directory"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Integer seed for reproducible output"),
) -> None:
    """Generate a relational bundle (customers, transactions, payments) with real
    foreign keys, one file per dataset."""
    import recordforge as rf

    try:
        docs = rf.generate_related(
            output=output, format=format, seed=seed,
            customers=customers, transactions=transactions, payments=payments,
        )
        for doc in docs:
            typer.echo(str(doc.path))
        typer.echo(f"\nGenerated {len(docs)} linked dataset(s).")
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


@app.command(name="generate-schema")
def generate_schema(
    schema: Path = typer.Option(..., "--schema", help="Path to a YAML or JSON schema file"),
    format: str = typer.Option("csv", "--format", help="Data format: xlsx | csv | json | jsonl"),
    output: Optional[Path] = typer.Option(None, "--output", help="Output directory"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Integer seed for reproducible output"),
) -> None:
    """Generate linked datasets from a schema file, with foreign keys resolved."""
    import recordforge as rf

    try:
        docs = rf.generate_schema(schema_path=schema, output=output, format=format, seed=seed)
        for doc in docs:
            typer.echo(str(doc.path))
        typer.echo(f"\nGenerated {len(docs)} dataset(s) from schema.")
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


@app.command(name="list-types")
def list_types() -> None:
    """Print all available document and data type keys."""
    import recordforge as rf

    from recordforge.core.dirty import DIRTY_TYPES

    types = rf.list_types()
    typer.echo("Document types (use with --format pdf | docx | html):")
    for t in types["documents"]:
        typer.echo(f"  {t}")
    typer.echo("\nData types (use with --format xlsx | csv | json | jsonl):")
    for t in types["data"]:
        typer.echo(f"  {t}")
    typer.echo("\nDirty error types (use with --dirty key=rate,...):")
    typer.echo(f"  {', '.join(DIRTY_TYPES)}")


@app.command()
def version() -> None:
    """Print the RecordForge version."""
    typer.echo(f"RecordForge {__version__}")
