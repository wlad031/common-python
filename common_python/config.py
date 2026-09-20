"""XDG configuration loading for command-line and TUI applications."""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any

import tomllib

from .xdg import config_path

CONFIG_FILENAMES = ("config.yml", "config.yaml", "config.toml")


def config_dir(app_name: str) -> Path:
    """Return app's XDG configuration directory."""
    return config_path(app_name)


def find_config_path(app_name: str, filename: str | None = None) -> Path | None:
    """Return first existing config file, preferring YAML then TOML."""
    filenames = (filename,) if filename else CONFIG_FILENAMES
    for name in filenames:
        path = config_path(app_name, name)
        if path.is_file():
            return path
    return None


def load_config(
    app_name: str,
    *,
    filename: str | None = None,
    defaults: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Load app config from XDG_CONFIG_HOME, merged onto optional defaults.

    With no explicit filename, searches ``config.yml``, ``config.yaml``, then
    ``config.toml``. Missing config returns a copy of ``defaults``.
    """
    config = deepcopy(dict(defaults or {}))
    path = find_config_path(app_name, filename)
    if path is None:
        return config
    return _merge(config, _load_mapping(path))


def keybindings(config: Mapping[str, Any], section: str = "keys") -> dict[str, str]:
    """Read a Textual-style binding-ID-to-key mapping from config."""
    values = config.get(section, {})
    if values is None:
        return {}
    if not isinstance(values, Mapping):
        raise ValueError(f"{section} must be a mapping of binding IDs to keys")

    bindings: dict[str, str] = {}
    for binding_id, key in values.items():
        if not isinstance(binding_id, str) or not binding_id.strip():
            raise ValueError(f"{section} binding ID must be a non-empty string")
        if not isinstance(key, str) or not key.strip():
            raise ValueError(f"{section}.{binding_id} must be a non-empty key string")
        bindings[binding_id] = key.strip()
    return bindings


def _load_mapping(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".toml":
        with path.open("rb") as file:
            value = tomllib.load(file)
    elif suffix in {".yml", ".yaml"}:
        try:
            import yaml
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "YAML config requires PyYAML; install common-python[config]"
            ) from exc
        with path.open(encoding="utf-8") as file:
            value = yaml.safe_load(file)
    else:
        raise ValueError(f"unsupported config format: {path}")

    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"config root must be a mapping: {path}")
    return dict(value)


def _merge(base: dict[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    for key, value in overlay.items():
        if isinstance(base.get(key), Mapping) and isinstance(value, Mapping):
            base[key] = _merge(dict(base[key]), value)
        else:
            base[key] = deepcopy(value)
    return base
