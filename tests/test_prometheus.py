import unittest

from common_python.prometheus import escape_label, render_labels


class PrometheusTest(unittest.TestCase):
    def test_escape_label(self):
        self.assertEqual(escape_label('one\\two\n"three"'), 'one\\\\two\\n\\"three\\"')

    def test_render_labels_is_sorted(self):
        self.assertEqual(
            render_labels({"zone": "a", "pool": "tank"}), '{pool="tank",zone="a"}'
        )
