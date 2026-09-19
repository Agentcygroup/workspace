"""Vault substitute: secrets encrypted at rest with a local key."""
from __future__ import annotations
import base64
import json
from pathlib import Path

KEY = b"sovereign-local-key-32-bytes!!!!"
STORE = Path(__file__).resolve().parent / "secrets.json"


def _xor(b: bytes) -> bytes:
    return bytes(x ^ KEY[i % len(KEY)] for i, x in enumerate(b))


def put(name: str, value: str) -> None:
    d = json.loads(STORE.read_text()) if STORE.exists() else {}
    d[name] = base64.b64encode(_xor(value.encode())).decode()
    STORE.write_text(json.dumps(d, indent=2))


def get(name: str) -> str | None:
    if not STORE.exists():
        return None
    d = json.loads(STORE.read_text())
    if name not in d:
        return None
    return _xor(base64.b64decode(d[name])).decode()


if __name__ == "__main__":
    put("api_key", "s3cr3t")
    assert get("api_key") == "s3cr3t"
    assert json.loads(STORE.read_text())["api_key"] != "s3cr3t"
    print("secrets ok")
