# common-python

[![License](https://img.shields.io/github/license/wlad031/common-python)](https://github.com/wlad031/common-python/blob/master/LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/wlad031/common-python)](https://github.com/wlad031/common-python/releases)

Small, dependency-light utilities shared by personal Python services. Keep modules narrow; add only primitives with multiple consumers.

## Install

Pin consumers to a release tag:

```bash
uv add "common-python @ git+https://github.com/wlad031/common-python.git@v0.3.0"
```

Core install has no third-party dependencies. Optional features:

```bash
uv add "common-python[flask] @ git+https://github.com/wlad031/common-python.git@v0.3.0"
uv add "common-python[lua] @ git+https://github.com/wlad031/common-python.git@v0.3.0"
```

## Modules

- `common_python.env` — strict environment parsing
- `common_python.http` — stdlib JSON HTTP requests and errors
- `common_python.prometheus` — label rendering and stdlib exporter handler
- `common_python.web` — optional Flask health, request logging, API-key auth

## Development

```bash
uv sync --extra flask
uv run python -m unittest discover -s tests
uv run ruff check .
```

## License

MIT. See [LICENSE](LICENSE).
