"""Parse the OmniTech corpus into a graph."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "specs" / "omnitech.md"
OUT = ROOT / "experiments" / "omnitech" / "graph.json"


def parse(text):
    nodes = []
    edges = []
    for i, line in enumerate(text.splitlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        nodes.append({"id": i, "label": line[:80]})
    return {"nodes": nodes, "edges": edges}


def main():
    text = SPEC_PATH.read_text()
    g = parse(text)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(g, indent=2))
    print(f"omnitech: {len(g['nodes'])} nodes")


if __name__ == "__main__":
    main()
