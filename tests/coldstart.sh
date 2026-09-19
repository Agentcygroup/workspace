#!/usr/bin/env bash
# Cold-start test: a fresh shell runs the four most-used commands and
# asserts each one produces the expected shape of output. Refuses if
# the README does not mention a command this test uses.
set -euo pipefail

cd "$(dirname "$0")/.."
. .venv/bin/activate 2>/dev/null || true

fail=0

assert_contains() {
  local label="$1"; shift
  local needle="$1"; shift
  local out
  out="$("$@" 2>&1 || true)"
  if echo "$out" | grep -qF "$needle"; then
    echo "  pass: $label"
  else
    echo "  FAIL: $label — expected to find: $needle"
    echo "$out" | head -10 | sed 's/^/    /'
    fail=1
  fi
}

echo "=== coldstart: README mentions the commands this test uses ==="
for cmd in "buildability.classify" "verify.sh" "autonomous_pipe.py" "standards/INDEX.json"; do
  if grep -qF "$cmd" README.md 2>/dev/null; then
    echo "  pass: README mentions $cmd"
  else
    echo "  FAIL: README does not mention $cmd"
    fail=1
  fi
done

echo
echo "=== coldstart: commands produce expected output ==="

assert_contains "classify UCI" "distribution:" \
  python -m buildability.classify mesh/specs_uci

assert_contains "verify.sh final line" "pass:" \
  ./scripts/verify.sh

assert_contains "pipe outcome" "passed:" \
  python pipe/autonomous_pipe.py

assert_contains "standards index" "generated:" \
  python -c "import json; d=json.load(open('standards/INDEX.json')); print('generated:', len(d.get('generated',[])))"

echo
if [ $fail -eq 0 ]; then
  echo "coldstart: PASS"
  exit 0
else
  echo "coldstart: FAIL"
  exit 1
fi
