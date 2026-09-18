#!/usr/bin/env bash
set -uo pipefail

ROOT="${1:-$HOME/workspace}"
REPORT="$ROOT/bootstrap_report.json"

if [ ! -d "$ROOT" ]; then
  echo "no workspace at $ROOT"
  exit 1
fi

cd "$ROOT"

echo "==> bootstrap: $ROOT"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
python -m pip install --quiet --upgrade pip
python -m pip install --quiet pytest

packages="core cli taxonomy hands ax agent_data kernel capstone capstone_flow hle portable"

total=0
passed=0
failed_packages=""

for pkg in $packages; do
  if [ ! -d "packages/$pkg" ]; then
    echo "  skip $pkg (not present)"
    continue
  fi
  total=$((total + 1))
  echo "  install $pkg"
  python -m pip install --quiet -e "packages/$pkg" 2>/dev/null || true
done

echo "==> running tests"
python -m pytest packages -q > /tmp/pytest_out.txt 2>&1
rc=$?

tail -3 /tmp/pytest_out.txt

if [ $rc -eq 0 ]; then
  passed=$total
  status="pass"
else
  status="fail"
  failed_packages="see /tmp/pytest_out.txt"
fi

python3 - <<PYEOF > "$REPORT"
import json, sys
report = {
    "root": "$ROOT",
    "packages_total": $total,
    "packages_installed": $passed,
    "status": "$status",
    "pytest_exit_code": $rc,
    "notes": "$failed_packages",
    "scoped_completion": $([ $rc -eq 0 ] && echo True || echo False),
    "unscoped_completion": "undefined"
}
print(json.dumps(report, indent=2))
PYEOF

cat "$REPORT"

if [ $rc -eq 0 ]; then
  echo "==> bootstrap ok"
  exit 0
else
  echo "==> bootstrap failed; see /tmp/pytest_out.txt"
  exit 1
fi
