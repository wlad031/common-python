import os
from pathlib import Path


def config_path(app_name: str, *parts: str) -> Path:
    return _xdg_home("XDG_CONFIG_HOME", ".config") / app_name / Path(*parts)


def data_path(app_name: str, *parts: str) -> Path:
    return _xdg_home("XDG_DATA_HOME", ".local/share") / app_name / Path(*parts)


def state_path(app_name: str, *parts: str) -> Path:
    return _xdg_home("XDG_STATE_HOME", ".local/state") / app_name / Path(*parts)


def ensure_parent(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _xdg_home(variable: str, fallback: str) -> Path:
    return Path(os.environ.get(variable, Path.home() / fallback))
