"""Parquet renderer via pyarrow.

pyarrow is an OPTIONAL dependency. It is deliberately not bundled in the Windows
installer (it is large), so Parquet output is available through pip and the CLI
only. Install it with: ``pip install "recordforge[parquet]"``.

The import is lazy — this module loads fine without pyarrow, and only a call to
``render`` raises a clear error when it is missing. That keeps pyarrow out of
the desktop PyInstaller build.
"""

import secrets
from pathlib import Path

from recordforge.core.faker_utils import sanitize_filename
from recordforge.core.models import GeneratedDoc


def _require_pyarrow():
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover - depends on optional install
        raise ValueError(
            'Writing Parquet needs pyarrow, which is not bundled in the Windows '
            'installer. Install it with: pip install "recordforge[parquet]" '
            "(or pip install pyarrow)."
        ) from exc
    return pa, pq


def render(dataset: str, rows: list[dict], output_dir: Path) -> GeneratedDoc:
    """Render dataset rows to a Parquet file (one column per field)."""
    pa, pq = _require_pyarrow()

    stem = sanitize_filename(f"{dataset}_{secrets.token_hex(3)}")
    path = output_dir / f"{stem}.parquet"

    columns = list(rows[0].keys()) if rows else ["note"]
    arrays, names = [], []
    for col in columns:
        values = [r.get(col) for r in rows]
        try:
            arr = pa.array(values)
        except (pa.ArrowInvalid, pa.ArrowTypeError, pa.ArrowNotImplementedError):
            # Mixed-type column (e.g. the edge_cases corpus): fall back to text
            # so any dataset still writes a valid Parquet file.
            arr = pa.array([None if v is None else str(v) for v in values])
        arrays.append(arr)
        names.append(col)

    pq.write_table(pa.Table.from_arrays(arrays, names=names), str(path))
    return GeneratedDoc(path=path, doc_type=dataset, format="parquet")
