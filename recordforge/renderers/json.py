"""JSON renderer for data types.

Writes a clean JSON array of row objects, UTF-8, pretty-printed.
Decimal and any non-native values are stringified via ``default=str``.
"""

import json as _json
import secrets
from pathlib import Path

from recordforge.core.faker_utils import sanitize_filename
from recordforge.core.models import GeneratedDoc


def render(dataset: str, rows: list[dict], output_dir: Path) -> GeneratedDoc:
    """Render dataset rows to a JSON file (array of objects)."""
    stem = sanitize_filename(f"{dataset}_{secrets.token_hex(3)}")
    path = output_dir / f"{stem}.json"

    with path.open("w", encoding="utf-8") as f:
        _json.dump(rows, f, indent=2, ensure_ascii=False, default=str)

    return GeneratedDoc(path=path, doc_type=dataset, format="json")
