"""Emit a stub spec for every kind in the ontology. Stubs are not implemented."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "packages" / "ontology" / "src"))
from ontology import LEVELS, KIND_INDEX

SPECS = ROOT / "mesh" / "specs"
SPECS.mkdir(parents=True, exist_ok=True)

DECLARATIVE = {"REGISTRY","LEDGER","ARTIFACT","GOVERNANCE","META"}

def run():
    written = 0
    for level, kinds in KIND_INDEX.items():
        for k in kinds:
            kind_id = f"{level[:6]}-{k}"
            spec = {
                "kind_id": kind_id,
                "level": level,
                "name": k,
                "status": "specified" if level in DECLARATIVE else "stub",
                "semantics": None,
                "emit": {"language": "python", "target": f"packages/{level.lower()}/src/"},
                "validator": None,
            }
            p = SPECS / (kind_id + ".json")
            p.write_text(json.dumps(spec, indent=2))
            written += 1
    return written

if __name__ == "__main__":
    n = run()
    print("wrote", n, "specs")
