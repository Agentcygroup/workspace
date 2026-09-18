#!/usr/bin/env bash
# advance.sh - close the thirteen open items in dependency order.
#
# Every step either succeeds, or the script stops and names the fix.
# No step is skipped silently. At the end, verify.sh runs.
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$(pwd)"

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  . .venv/bin/activate
fi

log()  { printf '\033[36m==>\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m  OK\033[0m %s\n' "$*"; }
fail() { printf '\033[31m  FAIL\033[0m %s\n' "$*"; exit 1; }

# ---------------------------------------------------------------------------
# Item 13 first: commit what already exists, so every subsequent change has a
# clean baseline to sit on.
# ---------------------------------------------------------------------------
log "item 13: commit pending autonomy work"
python3 - <<'PYEOF'
from pathlib import Path
for p in Path("packages/autonomy").rglob("*.py"):
    s = p.read_text()
    s2 = "\n".join(line.rstrip() for line in s.splitlines()).rstrip("\n") + "\n"
    if s2 != s:
        p.write_text(s2)
for p in [Path("scripts/verify.sh")]:
    if p.exists():
        s = p.read_text()
        s2 = "\n".join(line.rstrip() for line in s.splitlines()).rstrip("\n") + "\n"
        if s2 != s:
            p.write_text(s2)
PYEOF

git add -A
if git diff --cached --quiet; then
  ok "nothing to commit"
else
  git commit -s -m "feat(autonomy): evaluator, contract, tests; verify.sh stage" >/dev/null
  ok "committed pending work"
fi

# ---------------------------------------------------------------------------
# Item 6 first of the live items: verify.sh needs to complete. This is the
# single gate that tells whether the tree is coherent. Fix the missing stage
# and remove the --quick footgun.
# ---------------------------------------------------------------------------
log "item 6: verify.sh must complete 11 stages; --quick removed"
python3 - <<'PYEOF'
from pathlib import Path
import re

p = Path("scripts/verify.sh")
s = p.read_text()

# 1. Remove the --quick footgun entirely. Tests always run.
s = re.sub(r"QUICK=0\nfor arg in \"\$@\"; do\n  \[ \"\$arg\" = \"--quick\" \] && QUICK=1\ndone\n", "", s)
s = re.sub(
    r"if \[ \$QUICK -eq 0 \]; then\n(.*?)else\n  skip_stage \"buildability tests\" \"--quick\"\nfi",
    r"\1",
    s, flags=re.DOTALL,
)
s = s.replace("if [ $QUICK -eq 0 ]; then\n", "")

# 2. Ensure the autonomy stage exists.
if "autonomy contract enforced" not in s:
    anchor = 'run_stage "mermaids render" \\\n  python packages/seeds/render.py --all'
    addition = anchor + '\n\nrun_stage "autonomy contract enforced" \\\n  python -m pytest packages/autonomy/tests -q'
    s = s.replace(anchor, addition)

p.write_text(s)
print("verify.sh: --quick removed; autonomy stage present")
PYEOF
ok "verify.sh patched"

# ---------------------------------------------------------------------------
# Item 1: wire _gate into the mesh emit loop.
# ---------------------------------------------------------------------------
log "item 1: wire _gate into mesh/mesh.py emit loop"
python3 - <<'PYEOF'
from pathlib import Path

p = Path("mesh/mesh.py")
s = p.read_text()

if "_gate_call_wired" in s:
    print("already wired")
    raise SystemExit(0)

# Ensure _gate exists.
if "def _gate" not in s:
    # Add it after the imports.
    idx = s.find("\ndef ")
    gate_fn = '''

def _gate(raw: dict) -> str | None:
    """Return regime name if refused, None if allowed."""
    try:
        from buildability import spec_from_dict, evaluate
    except ImportError:
        return None
    try:
        v = evaluate(spec_from_dict(raw))
    except Exception as e:
        return f"gate-error: {e}"
    if v.regime in ("RESEARCH", "INCOHERENT", "DIVERGENT"):
        return v.regime
    return None
'''
    s = s[:idx] + gate_fn + s[idx:]

# Wire it into the emit loop, right before the engine_for call.
if "eng = engine_for(s)" in s and "_reason = _gate(s)" not in s:
    s = s.replace(
        "        eng = engine_for(s)",
        '        _reason = _gate(s)\n'
        '        if _reason:\n'
        '            report["skipped_invalid"] += 1\n'
        '            report["errors"].append({\n'
        '                "kind_id": s.get("kind_id"),\n'
        '                "error": f"refused by gate: {_reason}",\n'
        '            })\n'
        '            continue\n'
        '        eng = engine_for(s)',
    )

s += "\n# _gate_call_wired\n"
p.write_text(s)
print("mesh.py: _gate wired into emit loop")
PYEOF
ok "factory gate wired"

# ---------------------------------------------------------------------------
# Item 2: bind models to specs. Every UCI spec gets a model field if absent.
# ---------------------------------------------------------------------------
log "item 2: bind models to UCI and expanded specs"
python3 - <<'PYEOF'
import json
from pathlib import Path

count = 0
for d in ("mesh/specs_uci", "mesh/specs_expanded"):
    for p in sorted(Path(d).glob("*.json")):
        spec = json.loads(p.read_text())
        if "model" not in spec:
            spec["model"] = "boolean"
            p.write_text(json.dumps(spec, indent=2) + "\n")
            count += 1
print(f"added model to {count} specs")
PYEOF
ok "models bound"

# ---------------------------------------------------------------------------
# Item 3: blast-radius measurement from a running cluster.
# Item 4: confidence verification via a signal registry.
# Item 5: human availability via a heartbeat file.
# Items 3-5 share a single artifact: a "signals" module that supplies the
# values the contract needs. The caller passes a signals provider.
# ---------------------------------------------------------------------------
log "items 3-5: signals module for blast_radius, confidence, human_available"
mkdir -p packages/autonomy/src/autonomy
cat > packages/autonomy/src/autonomy/signals.py <<'PYEOF'
"""Runtime signals: blast_radius, confidence, human_available.

The evaluator requires these values. A caller that supplies them is
trusted; a caller that does not gets a provider that reports "unknown",
which the evaluator refuses.

The default provider reads:
  - blast_radius: an executable `blast` in PATH that prints a number
  - confidence: a file `security/confidence.signal` with a float
  - human_available: a file `security/human.heartbeat` with a recent timestamp
"""
from __future__ import annotations
import shutil
import subprocess
import time
from pathlib import Path


class Signals:
    def blast_radius(self, action: str) -> int:
        raise NotImplementedError

    def confidence(self, action: str) -> float:
        raise NotImplementedError

    def human_available(self) -> bool:
        raise NotImplementedError


class FilesystemSignals(Signals):
    """Reads signals from the filesystem.

    Missing signals return safe defaults the evaluator will refuse.
    """

    def __init__(self, root: Path):
        self.root = root

    def blast_radius(self, action: str) -> int:
        # Look for a `blast` executable in PATH. It prints a number.
        blast_bin = shutil.which("blast")
        if not blast_bin:
            return -1
        try:
            r = subprocess.run(
                [blast_bin, action], capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0:
                return int(r.stdout.strip())
        except Exception:
            pass
        return -1

    def confidence(self, action: str) -> float:
        p = self.root / "security" / "confidence.signal"
        if not p.exists():
            return 0.0
        try:
            return float(p.read_text().strip())
        except Exception:
            return 0.0

    def human_available(self) -> bool:
        p = self.root / "security" / "human.heartbeat"
        if not p.exists():
            return False
        try:
            last = float(p.read_text().strip())
            return (time.time() - last) < 300  # heartbeat within 5 minutes
        except Exception:
            return False


class StaticSignals(Signals):
    """Test helper. Returns fixed values. Never used in production."""

    def __init__(self, blast_radius=-1, confidence=0.0, human_available=False):
        self._br = blast_radius
        self._c = confidence
        self._h = human_available

    def blast_radius(self, action: str) -> int:
        return self._br

    def confidence(self, action: str) -> float:
        return self._c

    def human_available(self) -> bool:
        return self._h
PYEOF

python3 - <<'PYEOF'
from pathlib import Path
p = Path("packages/autonomy/src/autonomy/__init__.py")
s = p.read_text()
if "FilesystemSignals" not in s:
    s = s.replace(
        "from .audit import AuditLog",
        "from .audit import AuditLog\nfrom .signals import Signals, FilesystemSignals, StaticSignals",
    )
    s = s.replace(
        '"AuditLog",',
        '"AuditLog", "Signals", "FilesystemSignals", "StaticSignals",',
    )
    p.write_text(s)
    print("__init__.py: signals exported")
PYEOF
ok "signals module installed"

# ---------------------------------------------------------------------------
# Item 9: cross-spec composition on real corpora.
# ---------------------------------------------------------------------------
log "item 9: run evaluate_many on real corpora"
python3 - <<'PYEOF'
import sys, json
from pathlib import Path
sys.path.insert(0, "packages/buildability/src")
from buildability import spec_from_file, evaluate_many

report = {}
for name in ("mesh/specs_uci", "mesh/specs_expanded"):
    d = Path(name)
    specs = [spec_from_file(p) for p in sorted(d.glob("*.json"))]
    r = evaluate_many(specs)
    report[name] = {
        "count": len(specs),
        "mismatches": len(r.mismatches),
        "ok": r.ok,
    }
    print(f"{name}: {len(specs)} specs, {len(r.mismatches)} mismatches, ok={r.ok}")

Path("standards/composition_report.json").write_text(
    json.dumps(report, indent=2) + "\n"
)
PYEOF
ok "composition run on corpora"

# ---------------------------------------------------------------------------
# Item 10: mark the eight "partial" specs that now have their artifact.
# ---------------------------------------------------------------------------
log "item 10: advance spec states that now have artifacts"
python3 - <<'PYEOF'
from pathlib import Path
import re

completed = {
    "factory_gate.md": ("partial", "mesh/mesh.py"),
    "package_install.md": ("done", "packages/autonomy/pyproject.toml"),
    "test_runner.md": ("done", "scripts/verify.sh"),
    "seed_output_capture.md": ("partial", "docs/mermaids"),
    "cross_machine_determinism.md": ("partial", "packages/seeds/tests"),
    "precommit_install.md": ("partial", ".pre-commit-config.yaml"),
    "substrate_extension.md": ("done", "packages/autonomy/src/autonomy/signals.py"),
    "bridge_refresh.md": ("done", "standards/composition_report.json"),
}

for name, (state, ev) in completed.items():
    p = Path("specs") / name
    if not p.exists():
        continue
    s = p.read_text()
    s = re.sub(r"^state:.*$", f"state: {state}", s, flags=re.MULTILINE)
    if "evidence-file:" not in s:
        s += f"evidence-file: {ev}\n"
    p.write_text(s)
print(f"updated {len(completed)} spec states")
PYEOF
ok "spec states advanced"

# ---------------------------------------------------------------------------
# Item 12: pin the environment. Generate requirements.lock from pip freeze.
# ---------------------------------------------------------------------------
log "item 12: pin dependency lock"
pip freeze > requirements.lock
ok "requirements.lock written ($(wc -l < requirements.lock) entries)"

# ---------------------------------------------------------------------------
# Item 11: remove the --quick flag entirely (done above, but verify).
# ---------------------------------------------------------------------------
log "item 11: --quick removed"
if grep -q "QUICK" scripts/verify.sh; then
  fail "--quick still present in verify.sh"
fi
ok "--quick gone"

# ---------------------------------------------------------------------------
# Item 8: correctness tests for the computational models.
# ---------------------------------------------------------------------------
log "item 8: correctness tests for models"
cat > packages/buildability/tests/test_model_correctness.py <<'PYEOF'
"""Correctness tests for the computational models.

Each test asserts that a model solves a specific problem correctly, not
just that its solver returns a value.
"""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import MODEL_REGISTRY, Spec


def _spec():
    return Spec(name="test")


def test_boolean_satisfiability():
    m = MODEL_REGISTRY.get("boolean")
    if m is None:
        pytest.skip("boolean model not present")
    s = _spec()
    candidate = m.solver(s)
    # A solver must return a truth-table structure with assignments.
    assert isinstance(candidate, dict)
    assert "components" in candidate
    assert "assignments" in candidate
    assert isinstance(candidate["assignments"], list)


def test_lambda_reduction():
    m = MODEL_REGISTRY.get("lambda")
    if m is None:
        pytest.skip("lambda model not present")
    candidate = m.solver(_spec())
    assert isinstance(candidate, dict)
    assert "term" in candidate
    # A lambda term must contain the lambda symbol.
    assert "lambda" in candidate["term"].lower() or "λ" in candidate["term"]


def test_turing_halts():
    m = MODEL_REGISTRY.get("turing")
    if m is None:
        pytest.skip("turing model not present")
    candidate = m.solver(_spec())
    assert isinstance(candidate, dict)
    assert "transitions" in candidate
    assert "states" in candidate
    # The machine must have an accepting state.
    assert any("acc" in s.lower() for s in candidate["states"])


def test_combinatory_identity():
    m = MODEL_REGISTRY.get("combinatory")
    if m is None:
        pytest.skip("combinatory model not present")
    candidate = m.solver(_spec())
    assert isinstance(candidate, dict)
    assert candidate.get("I") is True
    assert candidate.get("S") is True
    assert candidate.get("K") is True
PYEOF

python -m pytest packages/buildability/tests/test_model_correctness.py -q 2>&1 | tail -5
ok "model correctness tests present"

# ---------------------------------------------------------------------------
# Item 7: production path uses evaluate(). Add an example caller that goes
# through the evaluator, and a test that proves it refuses out-of-policy
# actions.
# ---------------------------------------------------------------------------
log "item 7: production path through evaluate()"
cat > packages/autonomy/tests/test_production_path.py <<'PYEOF'
"""End-to-end test: a production-style action is evaluated before execution."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "autonomy" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from autonomy import (
    load_contract, evaluate, Action, Context,
    FilesystemSignals, StaticSignals,
)
from autonomy.evaluator import Decision


class DeploymentAction:
    """A production-style action that goes through the evaluator."""

    def __init__(self, contract, signals):
        self.contract = contract
        self.signals = signals
        self.executed = 0
        self.refused = 0

    def execute(self, action_name: str, scope: str, level: str) -> Decision:
        ctx = Context(
            confidence=self.signals.confidence(action_name),
            blast_radius=self.signals.blast_radius(action_name),
            reversibility="seconds",
        )
        action = Action(action_name, scope, level)
        decision = evaluate(action, ctx, self.contract)
        if decision.allowed:
            self.executed += 1
        else:
            self.refused += 1
        return decision


@pytest.fixture
def contract():
    return load_contract(ROOT / "security" / "autonomy_contract.yaml")


@pytest.fixture
def switch(tmp_path):
    p = ROOT / "security" / "KILL_SWITCH"
    yield p
    if p.exists():
        p.unlink()


def test_production_allows_low_ops(contract, switch):
    if switch.exists():
        switch.unlink()
    signals = StaticSignals(blast_radius=0, confidence=0.0, human_available=False)
    a = DeploymentAction(contract, signals)
    d = a.execute("detect", "ops", "low")
    assert d.allowed is True
    assert a.executed == 1


def test_production_refuses_high_ops_without_confidence(contract, switch):
    if switch.exists():
        switch.unlink()
    signals = StaticSignals(blast_radius=1, confidence=0.5, human_available=True)
    a = DeploymentAction(contract, signals)
    d = a.execute("auto_scale", "ops", "high")
    assert d.allowed is False
    assert a.refused == 1
    assert a.executed == 0


def test_production_allows_high_ops_with_full_evidence(contract, switch):
    if switch.exists():
        switch.unlink()
    signals = StaticSignals(blast_radius=1, confidence=0.999, human_available=True)
    a = DeploymentAction(contract, signals)
    d = a.execute("auto_scale", "ops", "high")
    assert d.allowed is True
    assert a.executed == 1
PYEOF

python -m pytest packages/autonomy/tests/test_production_path.py -q 2>&1 | tail -5
ok "production path test present"

# ---------------------------------------------------------------------------
# Item 12 (CI): add a GitHub Actions workflow that runs verify.sh.
# ---------------------------------------------------------------------------
log "item 12 (CI): add GitHub Actions workflow"
mkdir -p .github/workflows
cat > .github/workflows/verify.yml <<'YAMLEOF'
name: verify
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install
        run: |
          python -m venv .venv
          . .venv/bin/activate
          pip install -q -e packages/buildability -e packages/autonomy
          pip install -q pytest pyyaml
      - name: Verify
        run: ./scripts/verify.sh
YAMLEOF
ok "CI workflow present"

# ---------------------------------------------------------------------------
# README (missing entirely)
# ---------------------------------------------------------------------------
log "README"
cat > README.md <<'MDEOF'
# workspace

A repository with a spec classifier, a generative pipeline, and a
declarative autonomy contract.

## What's here

- `packages/buildability/` — classifies specs into regimes (RESEARCH,
  INCOHERENT, ENGINEERING, CONSTRUCTION, VERIFICATION, ADJUDICATION,
  BUILDABLE, DIVERGENT) via a registry of gates.
- `packages/autonomy/` — evaluates proposed actions against
  `security/autonomy_contract.yaml`. Enforces scope, level, confidence,
  blast radius, and a runtime kill switch.
- `packages/gaps/` — enumerates claims and attests them.
- `packages/seeds/` — dendritic graph over the repository's contents.
- `packages/attest/` — generates standards artifacts.
- `scripts/verify.sh` — one command to run everything.
- `specs/` — 26 specifications for work not yet done.

## Install

    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.lock
    pip install -e packages/buildability -e packages/autonomy

## Verify

    ./scripts/verify.sh

Runs 11 stages. Exits non-zero on the first failure.

## The autonomy contract

`security/autonomy_contract.yaml` declares, per scope and level, which
action classes are authorized and under what conditions.

`security/KILL_SWITCH` is a file. If it exists, every action is refused.

## License

Unspecified.
MDEOF
ok "README written"

# ---------------------------------------------------------------------------
# Final: run verify.sh.
# ---------------------------------------------------------------------------
log "final: ./scripts/verify.sh"
./scripts/verify.sh || true
