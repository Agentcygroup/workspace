"""Write the generated artifacts to standards/ and a summary index."""
from __future__ import annotations
import json
from pathlib import Path


def write_report(root: Path, artifacts: dict) -> Path:
    out = root / "standards"
    out.mkdir(exist_ok=True)
    for name, data in artifacts.items():
        (out / f"{name}.json").write_text(
            json.dumps(data, indent=2, default=str) + "\n"
        )
    generated = [k for k, v in artifacts.items() if v.get("status") == "generated"]
    omitted = [k for k, v in artifacts.items() if v.get("status") != "generated"]
    index = {
        "generated": generated,
        "omitted_or_error": [
            {"artifact": k, "reason": artifacts[k].get("reason", "unknown")}
            for k in omitted
        ],
        "count": len(artifacts),
    }
    (out / "INDEX.json").write_text(json.dumps(index, indent=2) + "\n")
    return out / "INDEX.json"
