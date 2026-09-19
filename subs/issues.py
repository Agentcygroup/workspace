"""Jira / Plane / OpenProject substitute: issues."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "issues.jsonl"
STATES = ["open", "in_progress", "resolved", "closed"]


def new(title: str, body: str = "") -> str:
    iid = f"i_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": iid, "title": title, "body": body,
                            "state": "open", "at": time.time()}) + "\n")
    return iid


def transition(iid: str, state: str) -> None:
    assert state in STATES
    with DB.open("a") as f:
        f.write(json.dumps({"id": iid, "state": state, "at": time.time()}) + "\n")


if __name__ == "__main__":
    i = new("fix login")
    transition(i, "in_progress")
    print("issues ok:", i)
