# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0](https://github.com/wlad031/shoutrrr-web/releases/tag/v0.2.0) - 2025-02-18

### Added
- Authentication can now be disabled by setting `AUTH_ENABLED` environment variable to `false` (default).

### Deprecated
- `X-Api-Key` header is deprecated in favor of `Authorization` header with `token api_key` format

## [0.1.0](https://github.com/wlad031/shoutrrr-web/releases/tag/v0.1.0) - 2025-02-12

### Added
- Initial release of common-python
- Blueprint for health check endpoint
  `GET /health` which returns `200 {"status": "healthy"}`
- Common logging configuration
- Logging for incoming requests
- Decorator for API key authentication
  Uses `X-Api-Key` header, acceptable keys are loaded from file configurable via `API_KEYS_FILE` environment variable


