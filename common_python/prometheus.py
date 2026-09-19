from __future__ import annotations

from collections.abc import Callable, Mapping
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse


def escape_label(value: object) -> str:
    """Escape a label value using Prometheus text exposition rules."""
    return str(value).replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def render_labels(labels: Mapping[str, object] | None = None) -> str:
    """Render deterministic Prometheus label syntax, including braces."""
    if not labels:
        return ""
    rendered = ",".join(
        f'{name}="{escape_label(value)}"' for name, value in sorted(labels.items())
    )
    return "{" + rendered + "}"


class PrometheusHandler(BaseHTTPRequestHandler):
    """Stdlib handler for /metrics, /healthz, and JSON 404 responses."""

    metrics_path = "/metrics"
    health_path = "/healthz"

    def collect_metrics(self) -> str:
        raise NotImplementedError

    def health_status(self) -> tuple[HTTPStatus, dict[str, object]]:
        return HTTPStatus.OK, {"status": "ok"}

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == self.metrics_path:
            self.send_text(
                HTTPStatus.OK, self.collect_metrics(), "text/plain; version=0.0.4"
            )
            return
        if path in ("/", self.health_path):
            status, payload = self.health_status()
            self.send_json(status, payload)
            return
        self.send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def send_text(
        self, status: HTTPStatus, body: str, content_type: str = "text/plain"
    ) -> None:
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        import json

        self.send_text(status, json.dumps(payload), "application/json")

    def log_message(self, _format: str, *_args: object) -> None:
        pass


def create_prometheus_handler(
    collector: Callable[[], str],
    health: Callable[[], tuple[HTTPStatus, dict[str, object]]] | None = None,
) -> type[PrometheusHandler]:
    """Create a configured handler class for ThreadingHTTPServer."""

    class Handler(PrometheusHandler):
        def collect_metrics(self) -> str:
            return collector()

        def health_status(self) -> tuple[HTTPStatus, dict[str, object]]:
            return health() if health else super().health_status()

    return Handler
