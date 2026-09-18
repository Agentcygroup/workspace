#!/usr/bin/env bash
set -uo pipefail
ROOT="${1:-$HOME/workspace}"
cd "$ROOT"
[ -d .venv ] && . .venv/bin/activate
python3 mesh/mesh.py
python3 -m pytest mesh/tests -q
