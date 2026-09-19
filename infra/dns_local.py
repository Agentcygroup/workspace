"""Cloudflare DNS substitute: a hosts map stored in JSON."""
from __future__ import annotations
import json
from pathlib import Path

MAP = Path(__file__).resolve().parent / "dns.json"


def resolve(name: str) -> str | None:
    if not MAP.exists():
        return None
    return json.loads(MAP.read_text()).get(name)


def register(name: str, ip: str) -> None:
    d = json.loads(MAP.read_text()) if MAP.exists() else {}
    d[name] = ip
    MAP.write_text(json.dumps(d, indent=2))


if __name__ == "__main__":
    register("api.sovereign", "127.0.0.1")
    register("ui.sovereign", "127.0.0.1")
    assert resolve("api.sovereign") == "127.0.0.1"
    print("dns ok")
