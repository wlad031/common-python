import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from common_python.config import find_config_path, keybindings, load_config


class ConfigTest(unittest.TestCase):
    def test_loads_toml_from_xdg_and_merges_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            config_file = Path(directory) / "demo" / "config.toml"
            config_file.parent.mkdir()
            config_file.write_text('[keys]\nrefresh = "ctrl+r"\n[ui]\ntheme = "dark"\n')

            with patch.dict(os.environ, {"XDG_CONFIG_HOME": directory}, clear=True):
                config = load_config(
                    "demo",
                    defaults={"keys": {"refresh": "r", "quit": "q"}, "ui": {}},
                )

        self.assertEqual(
            config,
            {
                "keys": {"refresh": "ctrl+r", "quit": "q"},
                "ui": {"theme": "dark"},
            },
        )

    def test_prefers_yaml_and_missing_config_returns_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            app_dir = Path(directory) / "demo"
            app_dir.mkdir()
            toml = app_dir / "config.toml"
            toml.write_text('value = "toml"\n')

            with patch.dict(os.environ, {"XDG_CONFIG_HOME": directory}, clear=True):
                self.assertEqual(find_config_path("demo"), toml)
                self.assertEqual(
                    load_config("missing", defaults={"value": "default"}),
                    {"value": "default"},
                )

    def test_keybindings_requires_string_mapping(self):
        self.assertEqual(
            keybindings({"keys": {"refresh": "ctrl+r"}}), {"refresh": "ctrl+r"}
        )
        with self.assertRaisesRegex(ValueError, "keys.refresh"):
            keybindings({"keys": {"refresh": 1}})
        with self.assertRaisesRegex(ValueError, "keys must be a mapping"):
            keybindings({"keys": "ctrl+r"})
