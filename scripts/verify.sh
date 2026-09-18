#!/usr/bin/env bash
# verify.sh - single entry point for repository verification.
#
# Runs every stage in order. Exits non-zero on the first failure.
# Prints a compact summary at the end.
#
# Usage:
#   ./scripts/verify.sh         # run all stages
#   ./scripts/verify.sh --quick # skip pytest (fast structural checks only)
set -u

cd "$(dirname "$0")/.."
ROOT="$(pwd)"

# Activate the venv if present so `python` resolves correctly.
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  . .venv/bin/activate
fi

# Fall back to python3 if `python` is not on PATH.
if ! command -v python >/dev/null 2>&1; then
  if command -v python3 >/dev/null 2>&1; then
    python() { python3 "$@"; }
    export -f python 2>/dev/null || true
  else
    echo "verify.sh: no python or python3 on PATH"
    exit 127
  fi
fi
QUICK=0
for arg in "$@"; do
  [ "$arg" = "--quick" ] && QUICK=1
done

PASS="\033[32mPASS\033[0m"
FAIL="\033[31mFAIL\033[0m"
SKIP="\033[33mSKIP\033[0m"

STAGES_PASS=0
STAGES_FAIL=0
STAGES_SKIP=0

run_stage() {
  local name="$1"
  shift
  printf '  %-40s ' "$name"
  local out
  out="$( "$@" 2>&1 )"
  local rc=$?
  if [ $rc -eq 0 ]; then
    printf "$PASS\n"
    STAGES_PASS=$((STAGES_PASS+1))
    return 0
  else
    printf "$FAIL\n"
    STAGES_FAIL=$((STAGES_FAIL+1))
    echo "$out" | sed 's/^/      /' | tail -20
    return 1
  fi
}

skip_stage() {
  local name="$1"
  local why="$2"
  printf '  %-40s ' "$name"
  printf "$SKIP  (%s)\n" "$why"
  STAGES_SKIP=$((STAGES_SKIP+1))
}

echo "==============================================================="
echo "verify.sh - $ROOT"
echo "==============================================================="
echo

# --- stage 1: buildability tests -------------------------------------------
if [ $QUICK -eq 0 ]; then
  run_stage "buildability tests" \
    python -m pytest packages/buildability/tests -q
else
  skip_stage "buildability tests" "--quick"
fi

# --- stage 2: standards artifacts regeneration -----------------------------
run_stage "standards artifacts regenerate" \
  python packages/attest/standards.py >/dev/null

run_stage "standards INDEX has no omissions" \
  python -c "
import json, sys
idx = json.load(open('standards/INDEX.json'))
if idx.get('omitted_or_error'):
    print('omitted:', idx['omitted_or_error']); sys.exit(1)
"

# --- stage 3: seed graph determinism ---------------------------------------
run_stage "seed graph is deterministic" \
  python -m pytest packages/seeds/tests -q

# --- stage 4: gap tool reports zero unattested -----------------------------
run_stage "gap tool: 0 unattested" \
  python -c "
import subprocess, json, sys
r = subprocess.run(['python','packages/gaps/gaps.py'], capture_output=True, text=True)
report = json.load(open('standards/attestation_gaps.json'))
n = report.get('unattested', 0)
if isinstance(n, list): n = len(n)
if n > 0:
    print('unattested:', n); sys.exit(1)
"

# --- stage 5: baseline stability -------------------------------------------
run_stage "baseline matches current state" \
  python scripts/baseline_check.py

# --- stage 6: spec-to-code inventory ---------------------------------------
run_stage "spec inventory is complete" \
  python scripts/inventory.py --check

# --- stage 7: complexity package imports -----------------------------------
run_stage "complexity package installs" \
  python -c "import complexity"

# --- stage 8: package exports are complete ---------------------------------
run_stage "attest exports complete" \
  python -c "from attest import Statement, Subject, build_statement, SBOM, generate_sbom"

# --- stage 9: mermaids are current -----------------------------------------
run_stage "mermaids render" \
  python packages/seeds/render.py --all

run_stage "autonomy contract enforced" \
  python -m pytest packages/autonomy/tests -q >/dev/null

echo
echo "==============================================================="
printf "  pass: %d   fail: %d   skip: %d\n" "$STAGES_PASS" "$STAGES_FAIL" "$STAGES_SKIP"
echo "==============================================================="

[ $STAGES_FAIL -eq 0 ]
