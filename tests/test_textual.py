import unittest

from textual.app import App, ComposeResult

from common_python.textual import (
    ManagedDataTable,
    TableColumn,
    TableRow,
    _table_cell,
    configured_table_columns,
)


class TableApp(App[None]):
    def compose(self) -> ComposeResult:
        yield ManagedDataTable(id="table")


class ConfiguredTableColumnsTests(unittest.TestCase):
    defaults = (
        TableColumn("name", "Name"),
        TableColumn("state", "State", 8),
        TableColumn("detail", "Detail"),
    )

    def test_configures_order_visibility_label_and_width(self) -> None:
        columns = configured_table_columns(
            {
                "columns": [
                    {"key": "state", "label": "Status", "width": 10},
                    {"key": "name"},
                    {"key": "detail", "visible": False},
                ]
            },
            self.defaults,
        )
        self.assertEqual(
            columns,
            (TableColumn("state", "Status", 10), TableColumn("name", "Name")),
        )

    def test_rejects_invalid_or_empty_column_config(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid column key"):
            configured_table_columns({"columns": [{"key": "missing"}]}, self.defaults)
        with self.assertRaisesRegex(ValueError, "at least one"):
            configured_table_columns(
                {"columns": [{"key": "name", "visible": False}]}, self.defaults
            )


class ManagedDataTableTests(unittest.IsolatedAsyncioTestCase):
    def test_exited_status_has_no_cell_background(self) -> None:
        self.assertEqual(_table_cell("exited (0)", False).style, "grey70")
        self.assertEqual(_table_cell("exited (1)", False).style, "bold red")

    async def test_manages_columns_keyboard_selection_and_refresh(self) -> None:
        app = TableApp()
        async with app.run_test() as pilot:
            table = app.query_one(ManagedDataTable)
            table.set_columns(
                (TableColumn("name", "Name"), TableColumn("state", "State"))
            )
            table.set_rows(
                (
                    TableRow("one", {"name": "alpha", "state": "UP"}, "first"),
                    TableRow("two", {"name": "bravo", "state": "DOWN"}, "second"),
                )
            )

            self.assertEqual(table.selected_key, "one")
            self.assertEqual(table.selected_data, "first")
            self.assertEqual(table.get_cell_at((0, 1)).style, "green")
            await pilot.press("j")
            self.assertEqual(table.selected_key, "two")
            self.assertEqual(table.selected_data, "second")

            table.set_rows(
                (
                    TableRow("two", {"name": "bravo", "state": "DOWN"}, "second"),
                    TableRow("one", {"name": "alpha", "state": "UP"}, "first"),
                )
            )
            self.assertEqual(table.selected_key, "two")
            self.assertEqual(table.cursor_row, 0)
            self.assertEqual(table.get_cell_at((0, 1)).plain, "DOWN")

            await pilot.press("j")
            self.assertEqual(table.selected_key, "one")
            await pilot.press("k")
            self.assertEqual(table.selected_key, "two")
