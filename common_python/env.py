import os

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off", ""}


def env_bool(name: str, default: bool = False) -> bool:
    """Read a strict boolean environment variable."""
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise ValueError(
        f"{name} must be one of: {', '.join(sorted(_TRUE_VALUES | _FALSE_VALUES))}"
    )


def env_int(name: str, default: int | None = None) -> int:
    """Read an integer environment variable, failing clearly when required."""
    value = _value_or_default(name, default)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def env_float(name: str, default: float | None = None) -> float:
    """Read a floating-point environment variable, failing clearly when required."""
    value = _value_or_default(name, default)
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


def load_dotenv(path: str = ".env", *, override: bool = False) -> None:
    """Load simple ``KEY=VALUE`` entries without shell evaluation.

    Supports optional ``export`` prefixes and single/double quoted values.
    Existing environment variables win unless ``override`` is true.
    """
    try:
        with open(path, encoding="utf-8") as file:
            lines = file
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:].lstrip()
                if "=" not in line:
                    continue
                name, value = line.split("=", 1)
                name = name.strip()
                value = value.strip()
                if not name:
                    continue
                if (
                    len(value) >= 2
                    and value[:1] == value[-1:]
                    and value[:1] in {"'", '"'}
                ):
                    value = value[1:-1]
                if override:
                    os.environ[name] = value
                else:
                    os.environ.setdefault(name, value)
    except FileNotFoundError:
        return


def required_env(name: str) -> str:
    """Read a non-empty environment variable."""
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"{name} is required")
    return value


def _value_or_default(name: str, default: int | float | None) -> str:
    value = os.getenv(name)
    if value is not None:
        return value
    if default is None:
        return required_env(name)
    return str(default)
