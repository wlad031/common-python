from collections.abc import Iterator
from contextlib import contextmanager

from rich.console import Console
from rich.status import Status


def console(json_mode: bool = False) -> Console:
    """Create a console safe for machine-readable JSON mode."""
    return Console(stderr=json_mode)


@contextmanager
def spinner(
    message: str, *, enabled: bool = True, output: Console | None = None
) -> Iterator[None]:
    """Show a transient spinner unless output is JSON/non-interactive."""
    if not enabled:
        yield
        return
    with (output or console()).status(Status(message)):
        yield
