"""Validation plus the run envelope.

Two functions matter here:

``check(payload)``  -> list of problems, never raises
``run(payload)``    -> Result, raises PayloadError when the contract is violated

The split exists so a caller can show a user what is missing before spending a
single token, instead of catching an exception and parsing its message.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .backend import Backend, default_backend
from .errors import CapError, PayloadError
from .spec import SPEC


@dataclass(frozen=True)
class Result:
    """What ``run()`` returns."""

    cap: str
    status: str
    backend: str
    data: Dict[str, Any] = field(default_factory=dict)
    note: str = ""
    elapsed_ms: float = 0.0

    def __bool__(self) -> bool:
        return self.status == "ok"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "cap": self.cap,
            "status": self.status,
            "backend": self.backend,
            "data": self.data,
            "note": self.note,
            "elapsed_ms": round(self.elapsed_ms, 3),
        }


def check(payload: Optional[Dict[str, Any]]) -> List[str]:
    """Return every contract violation in ``payload``. Empty list means valid."""
    problems: List[str] = []

    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        return [f"payload must be a dict, got {type(payload).__name__}"]

    missing = [p for p in SPEC.params if _blank(payload.get(p))]
    if missing:
        hint = f" ({SPEC.params_hint})" if SPEC.params_hint else ""
        problems.append(
            f"missing required parameter(s): {', '.join(missing)}{hint}"
        )

    if "op" in SPEC.params:
        op = payload.get("op")
        if op not in (None, "") and SPEC.ops and op not in SPEC.ops:
            problems.append(
                f"op={op!r} is not documented; known values: {', '.join(SPEC.ops)}"
            )

    return problems


def _blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def run(
    payload: Optional[Dict[str, Any]] = None,
    *,
    backend: Optional[Backend] = None,
    strict: bool = True,
) -> Result:
    """Validate ``payload`` and hand it to a backend.

    ``strict=True`` raises :class:`PayloadError` on a contract violation;
    ``strict=False`` runs anyway and records the problems in ``note``.
    """
    payload = dict(payload or {})
    problems = check(payload)
    if problems and strict:
        raise PayloadError(SPEC.name, problems)

    impl = backend if backend is not None else default_backend()
    started = time.perf_counter()
    data = impl.invoke(SPEC.name, payload)
    elapsed = (time.perf_counter() - started) * 1000.0

    if not isinstance(data, dict):
        raise CapError(
            f"{SPEC.name}: backend {impl.name!r} returned "
            f"{type(data).__name__}, expected dict"
        )

    stubbed = impl.name == "stub"
    status = "validated" if stubbed else "ok"
    note = ""
    if stubbed:
        note = (
            "payload checked against the contract; nothing was executed. "
            "Wire a backend to run it for real."
        )
    if problems:
        note = (note + " " if note else "") + "contract problems: " + "; ".join(problems)

    return Result(
        cap=SPEC.name,
        status=status,
        backend=impl.name,
        data=data,
        note=note,
        elapsed_ms=elapsed,
    )
