"""The run envelope must never dress a stub up as a success."""

from __future__ import annotations

import json

import pytest

from gbt_handoff import SPEC, run
from gbt_handoff.backend import Backend, default_backend, register_backend, reset_backend


def _payload():
    payload = {p: "x" for p in SPEC.params}
    if "op" in payload and SPEC.ops:
        payload["op"] = SPEC.ops[0]
    return payload


class Recording:
    name = "recording"

    def __init__(self):
        self.seen = None

    def invoke(self, cap, payload):
        self.seen = (cap, dict(payload))
        return {"received": len(payload)}


def test_default_backend_is_the_stub():
    reset_backend()
    assert default_backend().name == "stub"


def test_stub_reports_validated_not_ok():
    result = run(_payload())
    assert result.status == "validated"
    assert result.backend == "stub"
    assert result.data["executed"] is False
    assert not result, "a validated payload is not a successful execution"


def test_real_backend_reports_ok_and_is_actually_called():
    backend = Recording()
    result = run(_payload(), backend=backend)
    assert result.status == "ok"
    assert bool(result) is True
    assert backend.seen[0] == SPEC.name
    assert backend.seen[1] == _payload()


def test_registered_backend_becomes_the_default():
    backend = Recording()
    register_backend(backend)
    try:
        assert run(_payload()).backend == "recording"
    finally:
        reset_backend()


def test_register_rejects_objects_that_are_not_backends():
    with pytest.raises(TypeError):
        register_backend(object())


def test_backend_returning_a_non_dict_is_an_error():
    class Broken:
        name = "broken"

        def invoke(self, cap, payload):
            return ["nope"]

    with pytest.raises(Exception) as excinfo:
        run(_payload(), backend=Broken())
    assert "expected dict" in str(excinfo.value)


def test_result_is_json_serialisable():
    blob = json.dumps(run(_payload()).as_dict(), ensure_ascii=False)
    assert json.loads(blob)["cap"] == SPEC.name
