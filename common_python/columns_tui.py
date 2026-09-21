"""Declarative command-backed column TUI."""

from __future__ import annotations

import json
import shlex
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Static

from .columnar import ColumnarRow, ColumnarState
from .textual import MANAGED_TABLE_CSS, ManagedDataTable


@dataclass(frozen=True)
class Command:
    argv: tuple[str, ...] | None = None
    shell: str | None = None

    def run(self, values: Mapping[str, str] | None = None) -> str:
        if self.argv is not None:
            argv = (
                list(self.argv)
                if values is None
                else [part.format_map(values) for part in self.argv]
            )
            return subprocess.run(
                argv,
                check=True,
                text=True,
                capture_output=True,
            ).stdout
        assert self.shell is not None
        quoted = {key: shlex.quote(value) for key, value in (values or {}).items()}
        return subprocess.run(
            self.shell.format_map(quoted),
            shell=True,
            check=True,
            text=True,
            capture_output=True,
        ).stdout


@dataclass(frozen=True)
class Action:
    key: str
    title: str
    command: Command


@dataclass(frozen=True)
class ColumnsConfig:
    source: Command
    source_format: str
    watch: float
    columns: tuple[dict[str, Any], ...]
    actions: Mapping[str, Action]


def load_columns_config(path: str | Path) -> ColumnsConfig:
    raw = yaml.safe_load(Path(path).read_text())
    if not isinstance(raw, Mapping):
        raise ValueError("config must be YAML mapping")
    source_raw = raw.get("source")
    if not isinstance(source_raw, Mapping):
        raise ValueError("source must be mapping")
    source = _command(source_raw)
    columns = raw.get("columns", [])
    if not isinstance(columns, list):
        raise ValueError("columns must be list")
    actions_raw = raw.get("actions", {})
    if not isinstance(actions_raw, Mapping):
        raise ValueError("actions must be mapping")
    actions = {
        name: Action(
            str(item["key"]), str(item.get("title", name.title())), _command(item)
        )
        for name, item in actions_raw.items()
        if isinstance(item, Mapping) and "key" in item
    }
    return ColumnsConfig(
        source,
        str(source_raw.get("format", "jsonl")),
        float(source_raw.get("watch", 2)),
        tuple(columns),
        actions,
    )


def _command(raw: Mapping[str, Any]) -> Command:
    command = raw.get("command")
    shell = raw.get("shell")
    if isinstance(command, Sequence) and not isinstance(command, str) and not shell:
        return Command(tuple(str(part) for part in command))
    if isinstance(shell, str) and not command:
        return Command(shell=shell)
    raise ValueError("define exactly one of command or shell")


def parse_rows(
    output: str, output_format: str, columns: Sequence[Mapping[str, Any]] = ()
) -> tuple[ColumnarRow, ...]:
    values = (
        json.loads(output)
        if output_format == "json"
        else [json.loads(line) for line in output.splitlines() if line]
    )
    if not isinstance(values, list):
        raise ValueError("source JSON must be array")
    rows = []
    for index, value in enumerate(values):
        if not isinstance(value, Mapping):
            raise ValueError("source rows must be objects")
        source = {str(key): str(item) for key, item in value.items()}
        text, styles = _format_columns(source, columns)
        rows.append(
            ColumnarRow(
                source.get("ID", source.get("id", str(index))),
                text,
                value,
                styles=styles,
            )
        )
    return tuple(rows)


def _format_columns(
    source: Mapping[str, str], columns: Sequence[Mapping[str, Any]]
) -> tuple[dict[str, str], dict[str, str]]:
    if not columns:
        return dict(source), {}
    values, styles = {}, {}
    for column in columns:
        name = str(column["name"])
        values[name] = str(column.get("format", "{" + name + "}")).format_map(source)
        color = column.get("color")
        if isinstance(color, str):
            styles[name] = color.format_map(source)
    return values, styles


class ActionOutput(ModalScreen[None]):
    def __init__(self, title: str, output: str) -> None:
        super().__init__()
        self.title = title
        self.output = output

    def compose(self) -> ComposeResult:
        yield Static(self.title)
        with VerticalScroll():
            yield Static(self.output)

    def on_key(self, event: Key) -> None:
        if event.key in {"escape", "esc"}:
            self.dismiss()


class ColumnsTui(App[None]):
    CSS = MANAGED_TABLE_CSS + "#table { height: 1fr; } #summary { height: 1; }"
    BINDINGS = [Binding("q", "quit", "Quit"), Binding("r", "refresh", "Refresh")]

    def __init__(self, config: ColumnsConfig) -> None:
        super().__init__()
        self.config = config
        self.rows: tuple[ColumnarRow, ...] = ()

    def compose(self) -> ComposeResult:
        yield Static("Loading…", id="summary")
        yield ManagedDataTable(id="table", cursor_type="row", zebra_stripes=True)

    def on_mount(self) -> None:
        self.set_interval(self.config.watch, self.action_refresh)
        self.action_refresh()

    def action_refresh(self) -> None:
        self._refresh()

    @work(thread=True, exclusive=True)
    def _refresh(self) -> None:
        try:
            rows = parse_rows(
                self.config.source.run(), self.config.source_format, self.config.columns
            )
        except Exception as error:
            self.call_from_thread(self.notify, str(error), severity="error")
        else:
            self.call_from_thread(self._show_rows, rows)

    def on_key(self, event: Key) -> None:
        action = next(
            (item for item in self.config.actions.values() if item.key == event.key),
            None,
        )
        if action is None:
            return
        row = self.query_one("#table", ManagedDataTable).selected_data
        if isinstance(row, Mapping):
            self._run_action(
                action, {str(key): str(value) for key, value in row.items()}
            )
            event.stop()

    @work(thread=True)
    def _run_action(self, action: Action, values: Mapping[str, str]) -> None:
        try:
            output = action.command.run(values)
        except Exception as error:
            self.call_from_thread(self.notify, str(error), severity="error")
        else:
            self.call_from_thread(self.push_screen, ActionOutput(action.title, output))

    def _show_rows(self, rows: tuple[ColumnarRow, ...]) -> None:
        self.rows = rows
        table = self.query_one("#table", ManagedDataTable)
        table.set_configured_rows(
            ColumnarState().visible_rows(rows), {"columns": list(self.config.columns)}
        )
        self.query_one("#summary", Static).update(f"{len(rows)} rows")


def main(argv: Sequence[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args(argv)
    ColumnsTui(load_columns_config(args.config)).run()
