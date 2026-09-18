"""Core primitives."""
__version__ = "0.1.0"

def sha256_hex(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()

def canonical_json(obj) -> bytes:
    import json
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
