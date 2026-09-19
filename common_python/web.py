import hmac
import logging
import time
from collections.abc import Callable
from functools import wraps

from flask import Blueprint, Flask, Response, current_app, g, jsonify, request

from .env import env_bool


def configure_logging(app: Flask) -> None:
    """Configure request logging with method, path, response status, and latency."""
    logger = app.logger
    logger.setLevel(logging.INFO)
    if not any(
        getattr(handler, "_common_python", False) for handler in logger.handlers
    ):
        handler = logging.StreamHandler()
        handler._common_python = True  # type: ignore[attr-defined]
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.handlers = [handler]

    @app.before_request
    def start_request_timer() -> None:
        g.common_python_request_started = time.perf_counter()

    @app.after_request
    def log_response(response: Response) -> Response:
        if request.path != "/health":
            started = getattr(g, "common_python_request_started", time.perf_counter())
            latency_ms = (time.perf_counter() - started) * 1000
            logger.info(
                "%s %s status=%d latency_ms=%.1f remote=%s",
                request.method,
                request.path,
                response.status_code,
                latency_ms,
                request.remote_addr,
            )
        return response


def require_api_key(function: Callable) -> Callable:
    """Require a configured API key using constant-time comparison."""

    @wraps(function)
    def decorated(*args, **kwargs):
        auth_enabled, auth_keys = (
            current_app.config.get("auth_config") or load_auth_config()
        )
        if not auth_enabled:
            return function(*args, **kwargs)
        api_key = _request_api_key()
        if api_key is None:
            return jsonify({"status": "error", "message": "Missing API key"}), 401
        if not any(hmac.compare_digest(api_key, expected) for expected in auth_keys):
            return jsonify({"status": "error", "message": "Invalid API key"}), 401
        return function(*args, **kwargs)

    return decorated


def create_health_blueprint() -> Blueprint:
    """Return a Flask Blueprint that provides a /health endpoint."""
    health_blueprint = Blueprint("health", __name__)

    @health_blueprint.get("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    return health_blueprint


def log_request_info() -> None:
    """Compatibility no-op; configure_logging now logs after response completion."""


def load_auth_config() -> tuple[bool, list[str]]:
    """Load optional API-key authentication settings from environment variables."""
    if not env_bool("AUTH_ENABLED", default=False):
        result = False, []
    else:
        result = (
            True,
            load_api_keys(current_app.config.get("API_KEYS_FILE", "api_keys.txt")),
        )
    current_app.config["auth_config"] = result
    return result


def load_api_keys(filename: str) -> list[str]:
    """Load valid API keys from a file."""
    try:
        with open(filename, encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        current_app.logger.error("API keys file not found: %s", filename)
        return []


def _request_api_key() -> str | None:
    authorization = request.headers.get("Authorization", "")
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme != "token" or not token or " " in token:
            return None
        return token
    return request.headers.get("X-Api-Key")
