"""Factory controller: reads a blueprint, runs engines in stage order, writes a build report."""
import json, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLUEPRINTS = ROOT / "factory" / "blueprints"
BUILD = ROOT / "factory" / "build"
REPORT = BUILD / "factory_report.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engines import ENGINES

def load_blueprint(bid):
    p = BLUEPRINTS / (bid + ".json")
    if not p.exists():
        raise FileNotFoundError("blueprint not found: " + bid)
    return json.loads(p.read_text())

def run(bid="mesh.v1"):
    BUILD.mkdir(parents=True, exist_ok=True)
    bp = load_blueprint(bid)
    ctx = {"root": str(ROOT), "blueprint": bp}
    report = {
        "blueprint_id": bp["blueprint_id"],
        "version": bp["version"],
        "started_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "stages": [],
        "status": "pass",
        "invariants_checked": bp.get("invariants", []),
    }
    for s in bp["stages"]:
        eng = ENGINES.get(s["engine"])
        if eng is None:
            report["stages"].append({"id": s["id"], "name": s["name"], "status": "missing_engine"})
            report["status"] = "fail"
            continue
        try:
            r = eng(ctx)
            report["stages"].append({"id": s["id"], "name": s["name"], "status": "ok", "result": r})
        except Exception as e:
            report["stages"].append({"id": s["id"], "name": s["name"], "status": "fail", "error": str(e)})
            report["status"] = "fail"
    report["finished_utc"] = datetime.datetime.now(datetime.UTC).isoformat()
    REPORT.write_text(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    bid = sys.argv[1] if len(sys.argv) > 1 else "mesh.v1"
    r = run(bid)
    print(json.dumps({"blueprint_id": r["blueprint_id"], "status": r["status"], "stages": len(r["stages"])}, indent=2))
