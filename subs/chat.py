"""Slack / Mattermost / Rocket.Chat substitute: channels and messages."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "chat.jsonl"


def post(channel: str, who: str, text: str) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"channel": channel, "who": who,
                            "text": text, "at": time.time()}) + "\n")


def history(channel: str) -> list[dict]:
    if not DB.exists():
        return []
    return [json.loads(l) for l in DB.read_text().splitlines()
            if l.strip() and json.loads(l)["channel"] == channel]


if __name__ == "__main__":
    post("#general", "alice", "hello")
    post("#general", "bob", "hi")
    assert len(history("#general")) == 2
    print("chat ok")
