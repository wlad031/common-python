import os
import unittest
from unittest.mock import patch

from common_python.env import env_bool, env_float, env_int, required_env


class EnvTest(unittest.TestCase):
    def test_boolean_values(self):
        with patch.dict(os.environ, {"VALUE": "false"}, clear=True):
            self.assertFalse(env_bool("VALUE", default=True))
        with patch.dict(os.environ, {"VALUE": "yes"}, clear=True):
            self.assertTrue(env_bool("VALUE"))

    def test_invalid_boolean_fails(self):
        with (
            patch.dict(os.environ, {"VALUE": "sometimes"}, clear=True),
            self.assertRaises(ValueError),
        ):
            env_bool("VALUE")

    def test_numeric_values_and_required_value(self):
        with patch.dict(
            os.environ, {"COUNT": "2", "RATE": "1.5", "TOKEN": "x"}, clear=True
        ):
            self.assertEqual(env_int("COUNT"), 2)
            self.assertEqual(env_float("RATE"), 1.5)
            self.assertEqual(required_env("TOKEN"), "x")
