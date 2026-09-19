import json
import ssl
import urllib.error
import urllib.request
from typing import Any


class HttpRequestError(RuntimeError):
    """An HTTP request failed with transport, protocol, or JSON error."""


def request_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: Any = None,
    timeout: float = 10.0,
    context: ssl.SSLContext | None = None,
) -> Any:
    """Issue an stdlib HTTP request and decode its JSON response."""
    body = json.dumps(payload).encode() if payload is not None else None
    request_headers = {"Accept": "application/json", **(headers or {})}
    if body is not None:
        request_headers.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(
        url,
        data=body,
        headers=request_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(
            request, timeout=timeout, context=context
        ) as response:
            return json.loads(response.read().decode())
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        ValueError,
    ) as exc:
        raise HttpRequestError(f"{method} {url} failed: {exc}") from exc
