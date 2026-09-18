import json
from pathlib import Path

DECLARATIVE = {"REGISTRY","LEDGER","ARTIFACT","GOVERNANCE","META"}

def build(ctx):
    root = Path(ctx["root"])
    ontology_src = root / "packages" / "ontology" / "src"
    import sys
    sys.path.insert(0, str(ontology_src))
    from ontology import KIND_INDEX
    written = []
    specs_dir = root / "mesh" / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)
    count_spec = 0
    count_stub = 0
    for level, kinds in KIND_INDEX.items():
        for k in kinds:
            kind_id = f"{level[:6]}-{k}"
            status = "specified" if level in DECLARATIVE else "stub"
            spec = {
                "kind_id": kind_id,
                "level": level,
                "name": k,
                "status": status,
                "semantics": None,
                "emit": {"language": "python", "target": f"packages/{level.lower()}/src/"},
                "validator": None,
            }
            p = specs_dir / (kind_id + ".json")
            p.write_text(json.dumps(spec, indent=2))
            written.append(str(p))
            if status == "specified": count_spec += 1
            else: count_stub += 1
    return {"stage": "specs", "written": len(written), "specified": count_spec, "stub": count_stub}
