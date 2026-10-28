"""Contract tests: the package must reject what the registry says is incomplete."""

from __future__ import annotations

import pytest

from gbt_handoff import SPEC
from gbt_handoff.core import check, run
from gbt_handoff.errors import PayloadError


def test_non_dict_payload_is_reported():
    assert check(["not", "a", "dict"])


def test_empty_payload_matches_registry_expectation():
    problems = check({})
    if SPEC.params:
        assert problems, "required parameters exist, so {} must not validate"
    else:
        assert problems == []


@pytest.mark.parametrize("param", list(SPEC.params) or ["_no_params_"])
def test_each_required_param_is_actually_required(param):
    if param == "_no_params_":
        pytest.skip("this capability declares no required parameters")
    payload = _full()
    payload.pop(param)
    assert any(param in problem for problem in check(payload))


def test_full_payload_validates():
    assert check(_full()) == []


def _full():
    payload = {p: "x" for p in SPEC.params}
    if "op" in payload and SPEC.ops:
        payload["op"] = SPEC.ops[0]
    return payload


def test_strict_mode_raises_with_actionable_message():
    if not SPEC.params:
        pytest.skip("nothing to omit")
    with pytest.raises(PayloadError) as excinfo:
        run({})
    assert SPEC.params[0] in str(excinfo.value)


def test_unknown_op_is_rejected_when_ops_are_documented():
    if "op" not in SPEC.params or not SPEC.ops:
        pytest.skip("no documented op values")
    assert any("not documented" in p for p in check({"op": "__nope__", **{k: "x" for k in SPEC.params}}))
