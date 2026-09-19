import unittest

from common_python.lua import from_lua, to_lua


class FakeLua:
    def table_from(self, value):
        return value


class LuaTest(unittest.TestCase):
    def test_to_lua_recurses(self):
        self.assertEqual(
            to_lua(FakeLua(), {"items": [1, {"ok": True}]}),
            {"items": [1, {"ok": True}]},
        )

    def test_from_lua_converts_contiguous_numeric_keys_to_list(self):
        self.assertEqual(from_lua({1: "one", 2: {1: "two"}}), ["one", ["two"]])
