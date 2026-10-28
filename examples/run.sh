#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONPATH=src python -m gbt_handoff info
PYTHONPATH=src python -m gbt_handoff check --payload '{}'
PYTHONPATH=src python -m gbt_handoff run   --payload '{}'
