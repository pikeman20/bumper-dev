"""Provide base repository with common TinyDB operations."""

from typing import Any

from tinydb import Query
from tinydb.table import Document, Table

from .db import get_db
from .helpers import warn_if_not_doc


class BaseRepo:
    """Abstract base class for table-specific repos."""

    def __init__(self, table_name: str) -> None:
        self._table_name: str = table_name

    @property
    def table(self) -> Table:
        """Return the TinyDB table for this repo."""
        return get_db().table(self._table_name)

    def _upsert(self, data: dict[str, Any] | None, query: Query) -> list[int]:
        """Insert or update a record."""
        if data is None:
            return []
        return self.table.upsert(data, query)

    def _get(self, query: Query) -> Document | list[Document] | None:
        """Retrieve a document matching the query."""
        rec = self.table.get(query)
        warn_if_not_doc(rec, f"{self._table_name}.get result ({query.__dict__})")
        return rec

    def _remove(self, query: Query) -> None:
        """Remove a document matching the query."""
        rec = self.table.get(query)
        if isinstance(rec, Document):
            self.table.remove(doc_ids=[rec.doc_id])

    def update_list_field(self, query: Query, field: str, value: Any, add: bool) -> None:
        """Add or remove an item in a list field."""
        rec = self._get(query)
        if not isinstance(rec, Document):
            return
        lst = list(rec.get(field, []))
        if add and value not in lst:
            lst.append(value)
        elif not add and value in lst:
            lst.remove(value)
        self._upsert({field: lst}, query)
