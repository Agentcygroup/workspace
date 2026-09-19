"""Zendesk / Zammad substitute: support tickets."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "tickets.jsonl"


def open_(subject: str, requester: str) -> str:
    tid = f"t_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": tid, "subject": subject,
                            "requester": requester, "status": "open",
                            "at": time.time()}) + "\n")
    return tid


def close(tid: str, resolution: str) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"id": tid, "status": "closed",
                            "resolution": resolution,
                            "at": time.time()}) + "\n")


if __name__ == "__main__":
    t = open_("can't log in", "alice")
    close(t, "reset password")
    print("tickets ok")
