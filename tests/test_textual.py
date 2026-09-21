import unittest

from textual.app import App, ComposeResult

from common_python.textual import ManagedDataTable, TableColumn, TableRow


class TableApp(App[None]):
    def compose(self) -> ComposeResult:
        yield ManagedDataTable(id="table")


class ManagedDataTableTests(unittest.IsolatedAsyncioTestCase):
    async def test_manages_columns_keyboard_selection_and_refresh(self) -> None:
        app = TableApp()
        async with app.run_test() as pilot:
            table = app.query_one(ManagedDataTable)
            table.set_columns(
                (TableColumn("name", "Name"), TableColumn("state", "State"))
            )
            table.set_rows(
                (
                    TableRow("one", ("alpha", "UP"), "first"),
                    TableRow("two", ("bravo", "DOWN"), "second"),
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
                    TableRow("two", ("bravo", "DOWN"), "second"),
                    TableRow("one", ("alpha", "UP"), "first"),
                )
            )
            self.assertEqual(table.selected_key, "two")
            self.assertEqual(table.cursor_row, 0)
            self.assertEqual(table.get_cell_at((0, 1)).plain, "DOWN")

            await pilot.press("j")
            self.assertEqual(table.selected_key, "one")
            await pilot.press("k")
            self.assertEqual(table.selected_key, "two")
