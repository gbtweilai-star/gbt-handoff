"""Command line interface.

    $ python -m gbt_handoff info
    $ python -m gbt_handoff spec --json
    $ python -m gbt_handoff check --payload '{}'
    $ python -m gbt_handoff run   --payload '{}'

Exit codes: 0 ok, 1 contract violation, 2 bad usage.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Optional

from . import __version__
from .core import check, run
from .errors import CapError
from .spec import SPEC


def _load(raw: Optional[str]) -> Dict[str, Any]:
    if not raw:
        return {}
    if raw.startswith("@"):
        with open(raw[1:], "r", encoding="utf-8") as fh:
            raw = fh.read()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise SystemExit(f"payload must be a JSON object, got {type(value).__name__}")
    return value


def cmd_info(args: argparse.Namespace) -> int:
    print(f"{SPEC.name}  ({SPEC.domain})  v{__version__}")
    print("-" * max(40, len(SPEC.name) + 12))
    print(SPEC.desc)
    print()
    print(f"gated      : {SPEC.gated}" + ("   <- needs explicit consent" if SPEC.gated else ""))
    print(f"external   : {SPEC.external}")
    print(f"multi-op   : {SPEC.multi_op}")
    print(f"params     : {', '.join(SPEC.params) if SPEC.params else '(none)'}")
    if SPEC.params_hint:
        print(f"             {SPEC.params_hint}")
    if SPEC.ops:
        print(f"values     : {', '.join(SPEC.ops)}")
        if SPEC.ops_hint and SPEC.ops_hint != SPEC.params_hint:
            print(f"             {SPEC.ops_hint}")
    elif SPEC.multi_op:
        print("values     : (multi-op, but the registry does not enumerate them)")
    return 0


def cmd_spec(args: argparse.Namespace) -> int:
    data = SPEC.as_dict()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for key, value in data.items():
            print(f"{key:16} {value}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    problems = check(_load(args.payload))
    if not problems:
        print("ok: payload satisfies the contract")
        return 0
    print(f"rejected: {len(problems)} problem(s)")
    for problem in problems:
        print(f"  - {problem}")
    return 1


def cmd_run(args: argparse.Namespace) -> int:
    result = run(_load(args.payload))
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    return 0 if result.status in ("ok", "validated") else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m gbt_handoff",
        description=f"{SPEC.name} — {SPEC.summary}",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="verb", required=True)

    info = sub.add_parser("info", help="human-readable capability card")
    info.set_defaults(func=cmd_info)

    spec = sub.add_parser("spec", help="machine-readable contract")
    spec.add_argument("--json", action="store_true", help="emit JSON")
    spec.set_defaults(func=cmd_spec)

    for verb, func, text in (
        ("check", cmd_check, "validate a payload without executing"),
        ("run", cmd_run, "validate then execute"),
    ):
        p = sub.add_parser(verb, help=text)
        p.add_argument("--payload", default="{}", help="JSON object, or @file.json")
        p.set_defaults(func=func)

    return parser


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except CapError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: payload is not valid JSON ({exc})", file=sys.stderr)
        return 2
