import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from common_python.env import env_bool, env_float, env_int, load_dotenv, required_env


class EnvTest(unittest.TestCase):
    def test_boolean_values(self):
        with patch.dict(os.environ, {"VALUE": "false"}, clear=True):
            self.assertFalse(env_bool("VALUE", default=True))
        with patch.dict(os.environ, {"VALUE": "yes"}, clear=True):
            self.assertTrue(env_bool("VALUE"))

    def test_load_dotenv_preserves_existing_values(self):
        with tempfile.TemporaryDirectory() as directory:
            dotenv = Path(directory) / ".env"
            dotenv.write_text('FIRST=value\nexport SECOND="two words"\n')
            with patch.dict(os.environ, {"FIRST": "existing"}, clear=True):
                load_dotenv(str(dotenv))
                self.assertEqual(os.environ["FIRST"], "existing")
                self.assertEqual(os.environ["SECOND"], "two words")
                load_dotenv(str(dotenv), override=True)
                self.assertEqual(os.environ["FIRST"], "value")

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
