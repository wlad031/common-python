import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from flask import Flask

from common_python.web import require_api_key


class WebTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

        @self.app.get("/private")
        @require_api_key
        def private():
            return {"ok": True}

    def test_false_auth_environment_disables_authentication(self):
        with patch.dict(os.environ, {"AUTH_ENABLED": "false"}, clear=False):
            response = self.app.test_client().get("/private")

        self.assertEqual(response.status_code, 200)

    def test_token_authentication_uses_key_file(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            key_file = Path(temporary_dir) / "keys"
            key_file.write_text("expected-key\n", encoding="utf-8")
            self.app.config["API_KEYS_FILE"] = str(key_file)
            with patch.dict(os.environ, {"AUTH_ENABLED": "true"}, clear=False):
                allowed = self.app.test_client().get(
                    "/private", headers={"Authorization": "token expected-key"}
                )
                rejected = self.app.test_client().get(
                    "/private", headers={"Authorization": "token invalid"}
                )

        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(rejected.status_code, 401)
