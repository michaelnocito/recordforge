"""JSONL / NDJSON renderer for data types.

One JSON object per line, UTF-8 — the streaming format for Kafka, log
pipelines, and line-delimited ingestion. Decimal and any non-native
values are stringified via ``default=str``.
"""

import json as _json
import secrets
from pathlib import Path

from recordforge.core.faker_utils import sanitize_filename
from recordforge.core.models import GeneratedDoc


def render(dataset: str, rows: list[dict], output_dir: Path) -> GeneratedDoc:
    """Render dataset rows to a JSONL file (one object per line)."""
    stem = sanitize_filename(f"{dataset}_{secrets.token_hex(3)}")
    path = output_dir / f"{stem}.jsonl"

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(_json.dumps(row, ensure_ascii=False, default=str))
            f.write("\n")

    return GeneratedDoc(path=path, doc_type=dataset, format="jsonl")
