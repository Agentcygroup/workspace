"""Canva / Figma substitute: a design document as JSON."""
from __future__ import annotations
import json
import uuid
from pathlib import Path
DB = Path(__file__).resolve().parent / "designs.jsonl"


def new_doc(name: str, width: int = 1080, height: int = 1080) -> str:
    did = str(uuid.uuid4())
    with DB.open("a") as f:
        f.write(json.dumps({"id": did, "name": name,
                            "size": [width, height],
                            "layers": []}) + "\n")
    return did


def add_layer(did: str, kind: str, props: dict) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"id": did, "add_layer": {"kind": kind, "props": props}}) + "\n")


if __name__ == "__main__":
    d = new_doc("poster")
    add_layer(d, "rect", {"x": 0, "y": 0, "w": 100, "h": 100})
    print("design ok:", d)
