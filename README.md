# common-python

[![License](https://img.shields.io/github/license/wlad031/common-python)](https://github.com/wlad031/common-python/blob/master/LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/wlad031/common-python)](https://github.com/wlad031/common-python/releases)

Small, dependency-light utilities shared by personal Python services. Keep modules narrow; add only primitives with multiple consumers.

## Install

Pin consumers to a release tag:

```bash
uv add "common-python @ git+https://github.com/wlad031/common-python.git@v0.5.2"
```

Core install has no third-party dependencies. Optional features:

```bash
uv add "common-python[flask] @ git+https://github.com/wlad031/common-python.git@v0.5.2"
uv add "common-python[lua] @ git+https://github.com/wlad031/common-python.git@v0.5.2"
uv add "common-python[config] @ git+https://github.com/wlad031/common-python.git@v0.5.2"
```

## XDG app config and TUI keys

`common_python.config` loads `config.yml`, `config.yaml`, or `config.toml` from
`$XDG_CONFIG_HOME/<app>/` (default: `~/.config/<app>/`). YAML support needs
`common-python[config]`; TOML uses stdlib `tomllib`.

```yaml
# ~/.config/my-tui/config.yml
keys:
  refresh: ctrl+r
  quit: q
```

Use `load_config_file(path, defaults=...)` for explicit CLI config paths such
as `--config`, or `load_config_files(paths, defaults=...)` for ordered system,
user, profile, and explicit-override layers. Use `load_dotenv()` for simple,
non-shell-evaluated `.env` files.

For `CommonApp` subclasses, set `CONFIG_APP_NAME` and give each configurable
`Binding` a stable `id`. Config `keys` maps binding IDs to replacement keys.

```python
class MyApp(CommonApp):
    CONFIG_APP_NAME = "my-tui"
    BINDINGS = [Binding("r", "refresh", "Refresh", id="refresh")]
```

## Modules

- `common_python.config` — XDG YAML/TOML config loading and keybinding maps
- `common_python.env` — strict environment parsing
- `common_python.http` — stdlib JSON HTTP requests and errors
- `common_python.prometheus` — label rendering and stdlib exporter handler
- `common_python.web` — optional Flask health, request logging, API-key auth
- `common_python.lua` — optional Python/Lua table conversion
- `common_python.textual` — optional Textual shell and dialogs
- `common_python.columns_tui` — command-backed table TUI

## Table TUI

Install with Textual support, then pass source command directly. Plain text is one
row per line by default; use `--format jsonl` or `--format json` for structured rows:

```bash
uv tool install "common-python[textual] @ git+https://github.com/wlad031/common-python.git@v0.5.2"
table-tui run -- my-command --json
```

Interactive commands need non-interactive/batch mode. For `top`:

```bash
table-tui run -- top -b -n 1
```

Use `--watch SECONDS` to change refresh interval and `--timeout SECONDS` to cap
source execution. `columns-tui` remains alias for `table-tui`.

## Development

```bash
uv sync --extra flask
uv run python -m unittest discover -s tests
uv run ruff check .
```

## License

MIT. See [LICENSE](LICENSE).
