"""CSV renderer for data types.

Writes clean, directly-loadable CSV (header row + data rows), UTF-8.
No disclaimer row is injected so the file parses without special handling;
the fictional content and filename carry the "test data" signal.
"""

import csv as _csv
import secrets
from pathlib import Path

from recordforge.core.faker_utils import sanitize_filename
from recordforge.core.models import GeneratedDoc


def render(dataset: str, rows: list[dict], output_dir: Path) -> GeneratedDoc:
    """Render dataset rows to a CSV file."""
    stem = sanitize_filename(f"{dataset}_{secrets.token_hex(3)}")
    path = output_dir / f"{stem}.csv"

    headers = list(rows[0].keys()) if rows else ["note"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = _csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return GeneratedDoc(path=path, doc_type=dataset, format="csv")
