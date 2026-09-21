import unittest

from common_python.columnar import ColumnarRow, ColumnarState


class ColumnarStateTests(unittest.TestCase):
    rows = (
        ColumnarRow(
            "2",
            {"name": "redis", "status": "running"},
            filters={"status": "running"},
            sort_values={"name": "redis"},
        ),
        ColumnarRow(
            "1",
            {"name": "postgres", "status": "exited"},
            filters={"status": "exited"},
            sort_values={"name": "postgres"},
        ),
    )

    def test_filters_text_and_facets_then_sorts_stably(self) -> None:
        state = ColumnarState(
            query="post", filters={"status": {"exited"}}, sort_field="name"
        )
        self.assertEqual([row.key for row in state.visible_rows(self.rows)], ["1"])

    def test_empty_facet_selection_means_all_values(self) -> None:
        state = ColumnarState(sort_field="name", descending=True)
        self.assertEqual([row.key for row in state.visible_rows(self.rows)], ["2", "1"])
