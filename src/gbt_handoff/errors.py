"""Errors. Every failure mode is a named class, never a bare Exception."""

from __future__ import annotations

from typing import Any, List, Sequence


class CapError(Exception):
    """Base class for everything this package raises."""


class PayloadError(CapError):
    """The payload does not satisfy the capability contract."""

    def __init__(self, cap: str, problems: Sequence[str]) -> None:
        self.cap = cap
        self.problems: List[str] = list(problems)
        body = "\n".join(f"  - {p}" for p in self.problems)
        super().__init__(f"{cap}: payload rejected\n{body}")


class BackendRequired(CapError):
    """A real backend is required but none was supplied."""

    def __init__(self, cap: str) -> None:
        self.cap = cap
        super().__init__(
            f"{cap}: no backend is wired. This package publishes the contract; "
            f"execution needs an implementation of the Backend protocol. "
            f"Pass backend=... to run(), or install one that registers itself."
        )
