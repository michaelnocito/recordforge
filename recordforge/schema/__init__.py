"""Schema-driven relational generation.

Public surface:
- ``load_schema(path)`` -> validated ``Schema`` from a YAML or JSON file
- ``generate_datasets(rng, schema)`` -> ``{dataset_name: [row, ...]}`` with
  referential integrity (parents before children, no orphan foreign keys)
"""

from recordforge.schema.engine import generate_datasets, topo_order
from recordforge.schema.loader import load_schema
from recordforge.schema.models import Column, Dataset, Schema

__all__ = [
    "load_schema",
    "generate_datasets",
    "topo_order",
    "Schema",
    "Dataset",
    "Column",
]
