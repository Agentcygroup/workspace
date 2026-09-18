#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
. .venv/bin/activate 2>/dev/null || true
python -m attest.decide "$@"
python packages/attest/standards.py
