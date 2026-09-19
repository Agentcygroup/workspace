"""Redis substitute: dict with expiry, append-only log."""
from __future__ import annotations
import json
import time
from pathlib import Path

LOG = Path(__file__).resolve().parent / "kv.jsonl"
_store: dict[str, tuple[object, float | None]] = {}


def set_(k: str, v: object, ttl: float | None = None) -> None:
    expires = time.time() + ttl if ttl else None
    _store[k] = (v, expires)
    with LOG.open("a") as f:
        f.write(json.dumps({"op": "set", "k": k, "at": time.time()}) + "\n")


def get_(k: str):
    if k not in _store:
        return None
    v, exp = _store[k]
    if exp is not None and time.time() > exp:
        del _store[k]
        return None
    return v


def publish(channel: str, msg: object) -> None:
    with LOG.open("a") as f:
        f.write(json.dumps({"op": "pub", "ch": channel, "msg": msg,
                            "at": time.time()}) + "\n")


if __name__ == "__main__":
    set_("a", 1)
    set_("b", 2, ttl=0.05)
    assert get_("a") == 1
    time.sleep(0.1)
    assert get_("b") is None
    publish("alerts", {"sev": "warn"})
    print("kv ok")
