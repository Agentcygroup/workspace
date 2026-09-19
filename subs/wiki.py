"""Notion / AppFlowy / AnyType substitute: pages and blocks."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "wiki.jsonl"


def page(title: str, parent: str | None = None) -> str:
    pid = f"p_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": pid, "title": title,
                            "parent": parent, "blocks": [],
                            "at": time.time()}) + "\n")
    return pid


def add_block(pid: str, kind: str, text: str) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"id": pid, "add_block": {"kind": kind, "text": text},
                            "at": time.time()}) + "\n")


if __name__ == "__main__":
    p = page("home")
    add_block(p, "h1", "Welcome")
    print("wiki ok:", p)
