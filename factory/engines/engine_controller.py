from pathlib import Path

CONTROLLER = '''"""Mesh controller: reads specs, dispatches engines, writes report."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "mesh" / "specs"
EMITTED = ROOT / "mesh" / "emitted"
REPORT = ROOT / "mesh" / "report.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kinds import engine_for

def load_specs():
    out = []
    for p in sorted(SPECS.glob("*.json")):
        try:
            out.append(json.loads(p.read_text()))
        except Exception as e:
            out.append({"kind_id": p.stem, "status": "invalid", "error": str(e)})
    return out

def run():
    EMITTED.mkdir(parents=True, exist_ok=True)
    specs = load_specs()
    report = {"total": len(specs), "emitted": 0, "skipped_stub": 0, "skipped_invalid": 0, "failed": 0, "files": [], "errors": []}
    for s in specs:
        if s.get("status") == "invalid":
            report["skipped_invalid"] += 1
            report["errors"].append({"kind_id": s.get("kind_id"), "error": s.get("error")})
            continue
        if s.get("status") != "specified":
            report["skipped_stub"] += 1
            continue
        eng = engine_for(s)
        if eng is None:
            report["skipped_stub"] += 1
            continue
        try:
            written = eng(s, EMITTED / s["level"].lower())
            report["emitted"] += 1
            report["files"].extend(written)
        except Exception as e:
            report["failed"] += 1
            report["errors"].append({"kind_id": s.get("kind_id"), "error": str(e)})
    REPORT.write_text(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    r = run()
    print(json.dumps({k: r[k] for k in ("total","emitted","skipped_stub","skipped_invalid","failed")}, indent=2))
'''

def build(ctx):
    root = Path(ctx["root"])
    p = root / "mesh" / "mesh.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(CONTROLLER)
    return {"stage": "controller", "written": 1}
