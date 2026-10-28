"""The execution seam.

This package owns the *contract* for one capability bit: what it is called,
what it accepts, what it is allowed to touch. It deliberately does not own the
*implementation*, because the implementation lives in the GBT runtime this bit
was extracted from — a runtime with a 7.6B-parameter model, a consent store and
a machine attached to it.

So execution goes through a narrow protocol. Bring your own:

    class MyBackend:
        name = "my-backend"
        def invoke(self, cap, payload):
            return {"echo": payload}

    run({}, backend=MyBackend())

The default backend is a stub. It validates and returns, and it says so in the
result: ``status="validated"``, never ``"ok"``. A stub that reports success is
worse than no stub at all, because the caller stops looking.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Protocol, runtime_checkable


@runtime_checkable
class Backend(Protocol):
    """What a backend must look like."""

    name: str

    def invoke(self, cap: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ``cap`` with ``payload`` and return a JSON-serialisable dict."""
        ...


class StubBackend:
    """Validates the payload, executes nothing, and admits it."""

    name = "stub"

    def invoke(self, cap: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "executed": False,
            "reason": "no backend wired",
            "accepted_keys": sorted(payload),
        }


_DEFAULT: Optional[Backend] = None


def register_backend(backend: Backend) -> None:
    """Make ``backend`` the process-wide default for ``run()``."""
    global _DEFAULT
    if not isinstance(backend, Backend):
        raise TypeError(
            f"{type(backend).__name__} does not implement the Backend protocol "
            f"(needs a .name attribute and an .invoke(cap, payload) method)"
        )
    _DEFAULT = backend


def default_backend() -> Backend:
    return _DEFAULT if _DEFAULT is not None else StubBackend()


def reset_backend() -> None:
    """Drop the registered default. Used by tests; harmless in production."""
    global _DEFAULT
    _DEFAULT = None
