"""Data model and state engine for config-driven columnar TUIs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .textual import TableRow


@dataclass(frozen=True)
class ColumnarRow:
    """One source record. UI receives plain text plus optional metadata."""

    key: str
    values: Mapping[str, str]
    data: Any = None
    filters: Mapping[str, str] = field(default_factory=dict)
    sort_values: Mapping[str, Any] = field(default_factory=dict)

    def as_table_row(self) -> TableRow:
        return TableRow(self.key, self.values, self.data)


@dataclass
class ColumnarState:
    """Shared text filtering, facet filtering, stable sorting, and selection data."""

    query: str = ""
    filters: dict[str, set[str]] = field(default_factory=dict)
    sort_field: str | None = None
    descending: bool = False

    def visible_rows(self, rows: tuple[ColumnarRow, ...]) -> tuple[TableRow, ...]:
        needle = self.query.casefold()
        visible = [
            row
            for row in rows
            if needle in " ".join(row.values.values()).casefold()
            and self._matches_filters(row)
        ]
        if self.sort_field:
            field = self.sort_field
            visible.sort(key=lambda row: row.key)
            visible.sort(
                key=lambda row: row.sort_values.get(field, row.values.get(field, "")),
                reverse=self.descending,
            )
        return tuple(row.as_table_row() for row in visible)

    def _matches_filters(self, row: ColumnarRow) -> bool:
        return all(
            not enabled or row.filters.get(name) in enabled
            for name, enabled in self.filters.items()
        )
