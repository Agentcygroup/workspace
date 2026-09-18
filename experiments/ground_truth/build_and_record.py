"""Build systems from specs and record outcomes."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import spec_from_file, evaluate


def build(spec_path: Path) -> dict:
    spec = spec_from_file(spec_path)
    verdict = evaluate(spec)

    record = {
        "spec": spec_path.stem,
        "regime": verdict.regime,
        "components_declared": len(spec.components),
        "interfaces_declared": len(spec.interfaces),
        "build_attempted": False,
        "build_succeeded": False,
        "error": None,
    }

    try:
        if not spec.components:
            raise ValueError("no components to instantiate")
        if not spec.interfaces:
            raise ValueError("no interfaces to wire")

        instances = {}
        for comp in spec.components:
            if not comp.name or not comp.responsibility:
                raise ValueError("component " + repr(comp.name) + " incomplete")
            instances[comp.name] = {"responsibility": comp.responsibility}

        wiring = []
        for iface in spec.interfaces:
            if not iface.schema or not iface.protocol:
                raise ValueError("interface " + repr(iface.name) + " incomplete")
            wiring.append((iface.name, iface.schema, iface.protocol))

        record["build_attempted"] = True
        record["build_succeeded"] = True
        record["instances"] = list(instances.keys())
        record["wiring"] = wiring

    except Exception as e:
        record["build_attempted"] = True
        record["build_succeeded"] = False
        record["error"] = type(e).__name__ + ": " + str(e)

    return record


def main():
    specs = []
    passing = ROOT / "mesh" / "specs" / "DEMO-FULL.json"
    if passing.exists():
        specs.append(passing)
    failing = ROOT / "mesh" / "specs_expanded" / "EXPAND-L1-NO-INTERFACES.json"
    if failing.exists():
        specs.append(failing)
    sample = ROOT / "mesh" / "specs" / "INSTRU-NOP.json"
    if sample.exists():
        specs.append(sample)

    outcomes = [build(p) for p in specs]

    out = ROOT / "experiments" / "ground_truth" / "outcomes.json"
    out.write_text(json.dumps(outcomes, indent=2) + "\n")

    passed = sum(1 for o in outcomes if o["build_succeeded"])
    print("built " + str(passed) + "/" + str(len(outcomes)) + " systems")
    for o in outcomes:
        status = "OK " if o["build_succeeded"] else "FAIL"
        err = o["error"] or "-"
        print("  " + status + " " + o["spec"].ljust(40)
              + " regime=" + o["regime"].ljust(14) + " err=" + err)


if __name__ == "__main__":
    main()
