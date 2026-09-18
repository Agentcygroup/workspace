"""Entry point: python packages/attest/standards.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))

from attest import (
    collect, generate_all, write_report,
    load_decisions, generate_declared,
)

root = HERE.parent.parent
ev = collect(root)
artifacts = generate_all(ev)
decisions = load_decisions(root)
artifacts.update(generate_declared(decisions))
index = write_report(root, artifacts)

print(f"wrote {len(artifacts)} artifacts to {root / 'standards'}")
print(f"index: {index}")
for name, data in artifacts.items():
    status = data.get("status")
    if status == "generated":
        extra = ""
        if "count" in data:
            extra = f"  count={data['count']}"
        if "verified" in data:
            extra += f" verified={data['verified']}"
        if "conformant" in data:
            extra += f" conformant={data['conformant']}"
        print(f"  generated  {name}{extra}")
    else:
        print(f"  omitted    {name}: {data.get('reason')}")
