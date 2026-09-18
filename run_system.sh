#!/usr/bin/env bash
set -uo pipefail
ROOT="${1:-$HOME/workspace}"
cd "$ROOT"
[ -d .venv ] && . .venv/bin/activate
export PYTHONPATH="$ROOT/packages/core/src:$ROOT/packages/primitives/src:$ROOT/packages/lexicon/src:$ROOT/packages/kernel/src:$ROOT/packages/hands/src:$ROOT/packages/ax/src:$ROOT/packages/taxonomy/src:$ROOT/packages/standard/src"
python3 - <<'PY'
import json, sys
from pathlib import Path
report = {"steps": [], "status": "pass"}
def step(name, fn):
    try:
        r = fn()
        report["steps"].append({"step": name, "status": "ok", "result": r})
        print("ok  ", name, "->", r)
    except Exception as e:
        report["steps"].append({"step": name, "status": "fail", "error": str(e)})
        report["status"] = "fail"
        print("FAIL", name, "->", e)
from primitives import ATOMS, compose, validate_all as vp
step("primitives.load", lambda: len(ATOMS))
step("primitives.validate", lambda: vp())
from lexicon import TERMS
step("lexicon.load", lambda: len(TERMS))
from standard import conformance_report
step("standard.conformance", lambda: conformance_report()["standard_version"])
from hands import ALL_HAND_KINDS
step("hands.load", lambda: len(ALL_HAND_KINDS))
from ax import coverage
step("ax.coverage", lambda: coverage())
from taxonomy import LEVELS
step("taxonomy.load", lambda: len(LEVELS))
from kernel.envelope import make_envelope, verify_envelope
e = make_envelope("RUN-1","enterprise","fact.v1",{"a":1},provenance=["run"])
step("kernel.envelope", lambda: verify_envelope(e))
from kernel.mappings import map_envelope
m = map_envelope(make_envelope("RUN-2","physics","observable.v1",{"units":"m"},units={"x":"m"},provenance=["run"]),"physics_to_biology")
step("kernel.map", lambda: m.domain)
g = compose()
step("primitives.compose", lambda: {"nodes": g["node_count"], "edges": g["edge_count"]})
Path("system_report.json").write_text(json.dumps(report, indent=2))
print("\nstatus:", report["status"])
sys.exit(0 if report["status"]=="pass" else 1)
PY
