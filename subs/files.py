"""Box / Dropbox substitute: versioned file store."""
from __future__ import annotations
import hashlib
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parent / "files"
ROOT.mkdir(exist_ok=True)


def put(path: str, body: bytes) -> str:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(p.with_suffix(p.suffix + f".{time.time_ns()}"))
    p.write_bytes(body)
    return hashlib.sha256(body).hexdigest()


def get(path: str) -> bytes | None:
    p = ROOT / path
    return p.read_bytes() if p.exists() else None


def list_files() -> list[str]:
    return sorted(str(f.relative_to(ROOT)) for f in ROOT.rglob("*")
                  if f.is_file() and "." not in f.name)


if __name__ == "__main__":
    put("docs/readme.md", b"hello")
    assert get("docs/readme.md") == b"hello"
    print("files ok")
