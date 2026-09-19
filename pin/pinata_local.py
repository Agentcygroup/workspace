"""Pinata substitute: content-addressed local pin store."""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "pins"
ROOT.mkdir(exist_ok=True)
INDEX = ROOT / "index.jsonl"


def _hash(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def pin(data: bytes, name: str = "") -> str:
    h = _hash(data)
    p = ROOT / h.replace(":", "_")
    p.write_bytes(data)
    with INDEX.open("a") as f:
        f.write(json.dumps({"hash": h, "name": name, "at": time.time(),
                            "size": len(data)}) + "\n")
    return h


def get(h: str) -> bytes | None:
    p = ROOT / h.replace(":", "_")
    return p.read_bytes() if p.exists() else None


def list_pins() -> list[dict]:
    if not INDEX.exists():
        return []
    return [json.loads(l) for l in INDEX.read_text().splitlines() if l.strip()]


if __name__ == "__main__":
    h = pin(b"hello ipfs", name="greeting")
    assert get(h) == b"hello ipfs"
    assert any(p["hash"] == h for p in list_pins())
    print("pin ok:", h)
