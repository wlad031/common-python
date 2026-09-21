from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Middle
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label

from .config import keybindings, load_config

MANAGED_TABLE_CSS = """
DataTable { height: 1fr; background: transparent; }
DataTable > .datatable--header {
    color: magenta;
    text-style: bold;
    background: transparent;
}
DataTable > .datatable--cursor,
DataTable:focus > .datatable--cursor {
    background: #202020;
    color: #eeeeee;
    text-style: none;
}
"""


@dataclass(frozen=True)
class TableColumn:
    """Presentation metadata for one managed table column."""

    key: str
    label: str
    width: int | None = None


@dataclass(frozen=True)
class TableRow:
    """Application data rendered by :class:`ManagedDataTable`."""

    key: str
    cells: tuple[str, ...]
    data: Any = None


class ManagedDataTable(DataTable):
    """DataTable with Gatus-style presentation and stable keyboard selection."""

    DEFAULT_CSS = """
    ManagedDataTable { height: 1fr; background: transparent; }
    ManagedDataTable > .datatable--header {
        color: magenta;
        text-style: bold;
        background: transparent;
    }
    ManagedDataTable > .datatable--cursor,
    ManagedDataTable:focus > .datatable--cursor {
        background: #202020;
        color: #eeeeee;
        text-style: none;
    }
    """
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.selected_key: str | None = None
        self._row_data: dict[str, Any] = {}

    @property
    def selected_data(self) -> Any:
        """Payload associated with currently highlighted row, if any."""
        return self._row_data.get(self.selected_key) if self.selected_key else None

    def set_columns(self, columns: tuple[TableColumn, ...]) -> None:
        """Replace columns. Call :meth:`set_rows` afterwards to populate table."""
        self.clear(columns=True)
        for column in columns:
            self.add_column(column.label, key=column.key, width=column.width)

    def set_rows(self, rows: tuple[TableRow, ...]) -> None:
        """Replace rows while retaining highlighted row by stable key."""
        previous = self.selected_key or self._current_row_key()
        self.clear()
        self._row_data = {row.key: row.data for row in rows}
        keys: list[str] = []
        for row in rows:
            cells = tuple(_table_cell(value, row.data is None) for value in row.cells)
            self.add_row(*cells, key=row.key)
            keys.append(row.key)
        target = previous if previous in self._row_data else (keys[0] if keys else None)
        self.selected_key = target
        if target is not None:
            self.move_cursor(row=keys.index(target), animate=False, scroll=False)

    def action_cursor_down(self) -> None:
        super().action_cursor_down()
        self._sync_selected_key()

    def action_cursor_up(self) -> None:
        super().action_cursor_up()
        self._sync_selected_key()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if str(event.row_key.value) == self._current_row_key():
            self.selected_key = str(event.row_key.value)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_key = str(event.row_key.value)

    def _sync_selected_key(self) -> None:
        self.selected_key = self._current_row_key()

    def _current_row_key(self) -> str | None:
        if self.row_count == 0 or self.cursor_row is None:
            return None
        try:
            cell_key = self.coordinate_to_cell_key(self.cursor_coordinate)
            return str(cell_key.row_key.value)
        except Exception:
            return None


def _table_cell(value: str, is_group: bool) -> Text:
    if is_group:
        return Text(value, style="bold cyan")
    normalized = value.casefold()
    if normalized in {"up", "running"}:
        return Text(value, style="green")
    if normalized == "down":
        return Text(value, style="red")
    if normalized == "unknown":
        return Text(value, style="yellow")
    if normalized.startswith("exited ("):
        code = normalized.removeprefix("exited (").removesuffix(")")
        style = "grey70" if code == "0" else "bold red"
        return Text(value, style=style)
    return Text(value)


class CommonApp(App):
    """Shared Textual shell with optional XDG config-driven keybindings.

    Set ``CONFIG_APP_NAME`` in subclass and give configurable ``Binding`` objects
    stable ``id`` values. ``$XDG_CONFIG_HOME/<app>/config.yml`` may then map
    those IDs under ``keys``. TOML is accepted as ``config.toml`` fallback.
    """

    CONFIG_APP_NAME: ClassVar[str | None] = None
    CONFIG_FILENAME: ClassVar[str | None] = None
    CONFIG_DEFAULTS: ClassVar[dict[str, Any]] = {}
    CONFIG_KEY_SECTION: ClassVar[str] = "keys"

    CSS = """
    Screen { background: $surface; }
    #common-status { dock: bottom; padding: 0 1; color: $text-muted; }
    """
    BINDINGS = [Binding("r", "refresh", "Refresh", id="refresh")]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.config: dict[str, Any] = {}
        if self.CONFIG_APP_NAME:
            self.config = load_config(
                self.CONFIG_APP_NAME,
                filename=self.CONFIG_FILENAME,
                defaults=self.CONFIG_DEFAULTS,
            )
            self._bindings.apply_keymap(
                keybindings(self.config, self.CONFIG_KEY_SECTION)
            )

    def action_refresh(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        """Override in app-specific shell."""


class CommonTableApp(CommonApp):
    """Common ANSI terminal theme for apps built around ManagedDataTable."""

    CSS = """
    Screen { background: ansi_default; }
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("ansi_color", True)
        super().__init__(*args, **kwargs)
        self.theme = "ansi-dark"


class ConfirmDialog(ModalScreen[bool]):
    """Reusable destructive-action confirmation dialog."""

    CSS = """
    ConfirmDialog > Container {
        width: 60;
        height: auto;
        padding: 1 2;
        border: round $primary;
    }
    ConfirmDialog Button { margin: 1 1 0 0; }
    """
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("y", "confirm", "Confirm"),
        Binding("n", "cancel", "Cancel"),
    ]

    def __init__(self, message: str, confirm_label: str = "Confirm"):
        super().__init__()
        self.message = message
        self.confirm_label = confirm_label

    def compose(self) -> ComposeResult:
        with Center(), Middle(), Container():
            yield Label(self.message)
            yield Button(self.confirm_label, id="confirm", variant="error")
            yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


def periodic_refresh(app: CommonApp, interval_seconds: int) -> None:
    """Schedule refresh only for a positive interval."""
    if interval_seconds > 0:
        app.set_interval(interval_seconds, app.refresh_data)
