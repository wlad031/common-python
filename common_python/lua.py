"""Python/Lua table conversion helpers.

Requires ``common-python[lua]`` in the consuming application, but this module
imports no Lupa symbols so core installations remain dependency-free.
"""

from typing import Any


def to_lua(lua: Any, value: Any) -> Any:
    """Recursively convert dictionaries and lists into Lua tables."""
    if isinstance(value, dict):
        return lua.table_from({key: to_lua(lua, item) for key, item in value.items()})
    if isinstance(value, list):
        return lua.table_from([to_lua(lua, item) for item in value])
    return value


def from_lua(value: Any) -> Any:
    """Recursively convert Lua tables to dictionaries or contiguous lists."""
    if not hasattr(value, "items"):
        return value
    items = list(value.items())
    if items and all(isinstance(key, int) for key, _ in items):
        ordered = sorted((int(key), from_lua(item)) for key, item in items)
        if [key for key, _ in ordered] == list(range(1, len(ordered) + 1)):
            return [item for _, item in ordered]
    return {str(key): from_lua(item) for key, item in items}
