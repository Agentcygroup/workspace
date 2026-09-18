import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import spec_from_file, evaluate


SPEC = ROOT / "mesh" / "specs_counterexample" / "COUNTEREXAMPLE-DUPLICATE-OWNER.json"
OUT = ROOT / "experiments" / "central" / "counterexample_outcome.json"


spec = spec_from_file(SPEC)
verdict = evaluate(spec)

record = {
    "spec": spec.name,
    "regime": verdict.regime,
    "build_attempted": False,
    "build_succeeded": False,
    "reason": None,
}

if verdict.regime == "INCOHERENT":
    record["reason"] = "spec is incoherent; build refused by gate"
else:
    record["build_attempted"] = True
    record["build_succeeded"] = True
    record["reason"] = "gate did not refuse (unexpected)"

OUT.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
