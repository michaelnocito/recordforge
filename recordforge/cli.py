"""Typer CLI for RecordForge."""

from pathlib import Path
from typing import Optional

import typer

from recordforge import __version__

app = typer.Typer(name="recordforge", help="Generate synthetic documents and data files.")


@app.command()
def generate(
    type: str = typer.Option(..., "--type", help="Document or data type key"),
    format: str = typer.Option(
        ..., "--format", help="Documents: pdf | docx | html.  Data: xlsx | csv | json | jsonl"
    ),
    count: int = typer.Option(1, "--count", help="Number of files to generate (1–100)"),
    rows: int = typer.Option(50, "--rows", help="Rows per data file (ignored for documents)"),
    output: Optional[Path] = typer.Option(None, "--output", help="Output directory"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Integer seed for reproducible output"),
) -> None:
    """Generate synthetic documents or data files."""
    import recordforge as rf

    try:
        docs = rf.generate(
            type=type, format=format, count=count, output=output, seed=seed, rows=rows
        )
        for doc in docs:
            typer.echo(str(doc.path))
        typer.echo(f"\nGenerated {len(docs)} file(s).")
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


@app.command(name="list-types")
def list_types() -> None:
    """Print all available document and data type keys."""
    import recordforge as rf

    types = rf.list_types()
    typer.echo("Document types (use with --format pdf | docx | html):")
    for t in types["documents"]:
        typer.echo(f"  {t}")
    typer.echo("\nData types (use with --format xlsx):")
    for t in types["data"]:
        typer.echo(f"  {t}")


@app.command()
def version() -> None:
    """Print the RecordForge version."""
    typer.echo(f"RecordForge {__version__}")
