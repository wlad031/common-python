# Changelog

All notable changes to this project will be documented in this file.

## [0.5.0](https://github.com/wlad031/common-python/releases/tag/v0.5.0)

### Added
- XDG YAML/TOML config loading with deep-merged defaults.
- Configurable Textual binding IDs via `CommonApp`.

## [0.2.1](https://github.com/wlad031/common-python/releases/tag/v0.2.1) - 2025-02-21

This release doesn't have any significant changes, just some more logging for authentication debugging.

## [0.2.0](https://github.com/wlad031/common-python/releases/tag/v0.2.0) - 2025-02-18

### Added
- Authentication can now be disabled by setting `AUTH_ENABLED` environment variable to `false` (default).

### Deprecated
- `X-Api-Key` header is deprecated in favor of `Authorization` header with `token api_key` format

## [0.1.0](https://github.com/wlad031/common-python/releases/tag/v0.1.0) - 2025-02-12

### Added
- Initial release of common-python
- Blueprint for health check endpoint
  `GET /health` which returns `200 {"status": "healthy"}`
- Common logging configuration
- Logging for incoming requests
- Decorator for API key authentication
  Uses `X-Api-Key` header, acceptable keys are loaded from file configurable via `API_KEYS_FILE` environment variable


