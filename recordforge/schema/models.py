"""Dataclasses describing a RecordForge relational schema.

A Schema is a list of Datasets; each Dataset is a list of Columns. Columns
carry a type key (see recordforge.schema.columns) plus a free-form ``params``
dict for type-specific options (``ref`` for foreign keys, ``min``/``max`` for
numbers, and so on).
"""

from dataclasses import dataclass, field


@dataclass
class Column:
    """One column in a dataset."""

    name: str
    type: str
    params: dict = field(default_factory=dict)

    @property
    def ref(self) -> str | None:
        """Foreign-key target as ``table.column`` (fk columns only)."""
        return self.params.get("ref")

    @property
    def nullable(self) -> bool:
        return bool(self.params.get("nullable", False))


@dataclass
class Dataset:
    """A named table: a row count plus ordered columns."""

    name: str
    count: int
    columns: list[Column]


@dataclass
class Schema:
    """A full schema: a name plus ordered datasets."""

    name: str
    datasets: list[Dataset]

    def dataset(self, name: str) -> Dataset | None:
        """Return the dataset with this name, or None."""
        for ds in self.datasets:
            if ds.name == name:
                return ds
        return None
