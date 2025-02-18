import os
import logging
import re
from flask import Blueprint, jsonify, request, current_app
from functools import wraps


class HealthFilter(logging.Filter):
    def filter(self, record):
        return "/health" not in record.getMessage()


def configure_logging(app):
    """Configure logging for Flask and werkzeug."""
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.setLevel(logging.ERROR)
    health_filter = HealthFilter()
    for handler in werkzeug_logger.handlers:
        handler.addFilter(health_filter)
    flask_logger = logging.getLogger("flask-requests")
    flask_logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(health_filter)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    flask_logger.addHandler(console_handler)
    app.logger.handlers = [console_handler]
    app.logger.setLevel(logging.INFO)


def require_api_key(f):
    """Decorator that requires token authorization."""

    @wraps(f)
    def decorated(*args, **kwargs):
        cfg = current_app.config.get("auth_config", None)
        if not cfg:
            cfg = load_auth_config()
        auth_enabled, auth_keys = cfg
        if not auth_enabled:
            return f(*args, **kwargs)
        api_key = None
        token = request.headers.get("Authorization")
        if token:
            parts = token.split(" ")
            if len(parts) != 2:
                return jsonify({"status": "error", "message": "Invalid token"}), 401
            if parts[0] != "token":
                return jsonify({"status": "error", "message": "Invalid token"}), 401
            api_key = parts[1]
        else:
            api_key = request.headers.get("X-Api-Key")
            if api_key:
                current_app.logger.warning(
                    "Using deprecated X-Api-Key header, use Authorization header instead"
                )
        if not api_key:
            return jsonify({"status": "error", "message": "Missing token"}), 401
        if api_key not in auth_keys:
            return jsonify({"status": "error", "message": "Invalid API key"}), 401
        return f(*args, **kwargs)

    return decorated


def create_health_blueprint():
    """Return a Flask Blueprint that provides a /health endpoint."""
    health_bp = Blueprint("health", __name__)

    @health_bp.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy"}), 200

    return health_bp


def log_request_info():
    """Log request information excluding the /health endpoint."""
    if request.path != "/health":
        current_app.logger.info("Request Body: %s", request.get_data(as_text=True))
        current_app.logger.info("Request Sender: %s", request.remote_addr)


def load_auth_config():
    """Load auth configuration from environment variables."""
    result = False, []
    if not os.getenv("AUTH_ENABLED", False):
        current_app.logger.warning("Auth disabled")
    else:
        api_keys_file = os.getenv("API_KEYS_FILE", "api_keys.txt")
        result = True, load_api_keys(api_keys_file)
    current_app.config["auth_config"] = result
    return result


def load_api_keys(filename):
    """Load valid API keys from a file."""
    try:
        current_app.logger.info("Loading API keys from %s", filename)
        with open(filename, "r") as f:
            keys = [line.strip() for line in f if line.strip()]
            current_app.logger.info("Loaded %d API keys", len(keys))
        return keys
    except FileNotFoundError:
        current_app.logger.error("API keys file not found: %s", filename)
        return []
