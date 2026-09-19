"""Intercom / Chatwoot substitute: chat transcripts."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "chats.jsonl"


def open_(user: str) -> str:
    cid = f"c_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": cid, "user": user,
                            "msgs": [], "at": time.time()}) + "\n")
    return cid


def say(cid: str, who: str, text: str) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"id": cid, "add_msg": {"who": who, "text": text},
                            "at": time.time()}) + "\n")


if __name__ == "__main__":
    c = open_("alice")
    say(c, "alice", "hi")
    say(c, "agent", "hello")
    print("support_chat ok:", c)
