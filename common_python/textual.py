from __future__ import annotations

from typing import Any, ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Middle
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from .config import keybindings, load_config


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
