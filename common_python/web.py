import os
import logging
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
    """Decorator that requires the X-Api-Key header to be valid."""

    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-Api-Key")
        if not api_key:
            return jsonify({"status": "error", "message": "Missing API key"}), 401
        valid_keys = load_api_keys()
        if api_key not in valid_keys:
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


def load_api_keys(filename=None):
    """Load valid API keys from a file."""
    if not filename:
        filename = os.getenv("API_KEYS_FILE", "api_keys.txt")
    try:
        current_app.logger.info("Loading API keys from %s", filename)
        with open(filename, "r") as f:
            keys = [line.strip() for line in f if line.strip()]
            current_app.logger.info("Loaded %d API keys", len(keys))
        return keys
    except FileNotFoundError:
        current_app.logger.error("API keys file not found: %s", filename)
        return []
