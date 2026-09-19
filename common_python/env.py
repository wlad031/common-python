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
