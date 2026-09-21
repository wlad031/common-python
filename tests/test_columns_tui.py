import unittest
from unittest.mock import patch

from common_python.columnar import ColumnarRow
from common_python.columns_tui import (
    ColumnsConfig,
    ColumnsTui,
    Command,
    build_parser,
    main,
)


class ColumnsTuiCliTests(unittest.TestCase):
    def test_run_command_parses_source_command(self) -> None:
        args = build_parser().parse_args(
            ["run", "--format", "json", "--", "tool", "list", "--json"]
        )
        self.assertEqual(args.command, "run")
        self.assertEqual(args.output_format, "json")
        self.assertEqual(args.source_command, ["--", "tool", "list", "--json"])

    def test_main_runs_source_command(self) -> None:
        with patch("common_python.columns_tui.run") as run:
            main(["run", "--", "tool", "list"])
        run.assert_called_once_with(["tool", "list"], "text", 2, 5)


class ColumnsTuiTests(unittest.IsolatedAsyncioTestCase):
    async def test_renders_rows_without_column_configuration(self) -> None:
        app = ColumnsTui(
            ColumnsConfig(Command(("printf", "")), "text", 60, (), {})
        )
        async with app.run_test():
            app._show_rows((ColumnarRow("row", {"output": "value"}, {}),))
            self.assertEqual(app.query_one("#table").row_count, 1)
