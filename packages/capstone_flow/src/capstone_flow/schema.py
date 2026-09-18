import json
from pathlib import Path
from . import flow, verify_flow


def build_all(dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    f = flow("INST-HOSPITAL", "INST-STANDARDS", "INST-UNIVERSITY")
    p = dest / "flow.json"
    p.write_text(json.dumps(f, indent=2))
    p2 = dest / "flow_validation.json"
    p2.write_text(json.dumps({"errors": verify_flow(f)}, indent=2))
    return [str(p), str(p2)]
