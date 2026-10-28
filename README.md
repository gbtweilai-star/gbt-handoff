# handoff

**One capability bit from GBT V8, packaged standalone.** No. 263 of 341,
`system` domain (System).

<p>
<img alt="python" src="https://img.shields.io/badge/python-3.9%2B-blue">
<img alt="license" src="https://img.shields.io/badge/license-MIT-green">
<img alt="deps" src="https://img.shields.io/badge/runtime%20dependencies-0-brightgreen">
</p>

> 跨体接续包（ai-memory #08 蒸馏）：三桶=架构背景/失败尝试/未完成任务（缺桶必须显式空数组）；**没 src 不收**（传闻不入账）；只追加不删（作废走 retract）；read 给『每桶最新一条 + 未完成计数』供接手第一眼。op=write/read/retract/verify/where

That description is copied verbatim from the registry. `tests/test_spec.py` pins it,
so documentation drift fails the build instead of shipping quietly.

## What this package actually is

It is the **contract** for one capability: its name, its parameters, the values it
accepts, and whether it can change state that cannot be restored. It is not the
implementation — that lives in the runtime this bit was extracted from.

So `run()` goes through a narrow `Backend` protocol, and the default backend is a
stub that **says so**:

```
status="validated"   backend="stub"   data={"executed": false}
```

Never `status="ok"`. A stub that reports success is worse than no stub, because the
caller stops looking for the real thing.

## Install

```bash
git clone https://github.com/gbtweilai-star/gbt-handoff.git
cd gbt-handoff
python -m pip install -e ".[dev]"
```

## Use

```bash
python -m gbt_handoff info                  # capability card
python -m gbt_handoff spec --json           # machine-readable contract
python -m gbt_handoff check --payload '{}'
python -m gbt_handoff run   --payload '{}'
```

Real `info` output from this machine:

```text
handoff  (system)  v1.0.0
----------------------------------------
跨体接续包（ai-memory #08 蒸馏）：三桶=架构背景/失败尝试/未完成任务（缺桶必须显式空数组）；**没 src 不收**（传闻不入账）；只追加不删（作废走 retract）；read 给『每桶最新一条 + 未完成计数』供接手第一眼。op=write/read/retract/verify/where

gated      : False
external   : False
multi-op   : True
params     : (none)
values     : write, read, retract, verify, where
```

Wire a real implementation:

```python
from gbt_handoff import run

class MyBackend:
    name = "my-backend"
    def invoke(self, cap, payload):
        return {"cap": cap, "handled": sorted(payload)}

result = run({}, backend=MyBackend())
assert result.status == "ok"
```

## Parameters

| name | required | notes |
|---|---|---|
| — | no | the registry declares no required parameters |

Registry hint (`params_hint`): (empty)

**注册表登记的取值 / 子动作（5 个）**：`write`、`read`、`retract`、`verify`、`where`

Types are deliberately absent: the registry does not declare them, and an invented
type is worse than no type, because callers believe it.

## Boundaries

- Not gated: the registry marks this bit `safe: true`.
- No external service dependency declared.
- Multi-op (`multi_op: true`): several sub-actions share one name — read `op` before calling.
- No implementation ships here. Bring a backend; the protocol is one method.

## What this is not

Not a wrapper around a hosted API. Not a model. Not a promise that calling it does
anything on its own. It is the typed seam plus the validation, which is the part that
stays correct even when the implementation changes.

## Tests

```bash
python -m pytest
```

```text
20 passed, 3 skipped in 0.17s
```

## Provenance

| field | value |
|---|---|
| capability | `handoff` |
| domain | `system` |
| handler | `handoff` |
| safe | `True` (gated = `False`) |
| external | `False` |
| atlas page | [system/handoff](https://github.com/gbtweilai-star/gbt-caps/blob/main/caps/system/handoff.md) |
| full index | [https://github.com/gbtweilai-star/gbt-caps](https://github.com/gbtweilai-star/gbt-caps) |

The parent README says 348 capabilities; an AST pass over the registry enumerates
`341 + 0 unimplemented + 0 disabled = 341`. The extra 7 are historical duplicates.
Numbering here follows 341 and matches the `gbt-caps` index one-to-one.

## License

MIT.
