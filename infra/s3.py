"""S3 / R2 substitute: filesystem object store with versioning."""
from __future__ import annotations
import hashlib
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "objects"
ROOT.mkdir(exist_ok=True)


def _key(bucket: str, name: str) -> Path:
    d = ROOT / bucket
    d.mkdir(exist_ok=True)
    return d / name


def put(bucket: str, name: str, body: bytes) -> dict:
    p = _key(bucket, name)
    h = hashlib.sha256(body).hexdigest()
    if p.exists():
        version = p.with_suffix(p.suffix + f".{time.time_ns()}.{h[:12]}")
        p.rename(version)
    p.write_bytes(body)
    return {"bucket": bucket, "name": name, "sha256": h, "size": len(body)}


def get(bucket: str, name: str) -> bytes | None:
    p = _key(bucket, name)
    return p.read_bytes() if p.exists() else None


def list_objects(bucket: str) -> list[str]:
    d = ROOT / bucket
    if not d.exists():
        return []
    return sorted(f.name for f in d.iterdir() if "." not in f.suffix)


if __name__ == "__main__":
    put("assets", "hello.txt", b"world")
    put("assets", "hello.txt", b"world2")
    assert get("assets", "hello.txt") == b"world2"
    assert "hello.txt" in list_objects("assets")
    print("s3 ok")
