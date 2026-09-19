"""Mailchimp / Listmonk substitute: campaign list and dispatch log."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "campaigns.jsonl"


def subscribe(email: str) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"op": "subscribe", "email": email,
                            "at": time.time()}) + "\n")


def campaign(subject: str, body: str) -> str:
    cid = f"c_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"op": "campaign", "id": cid,
                            "subject": subject, "body": body,
                            "at": time.time()}) + "\n")
    return cid


def subscribers() -> list[str]:
    if not DB.exists():
        return []
    out = []
    for l in DB.read_text().splitlines():
        if not l.strip():
            continue
        e = json.loads(l)
        if e["op"] == "subscribe":
            out.append(e["email"])
    return out


if __name__ == "__main__":
    subscribe("alice@example.com")
    c = campaign("hello", "body")
    assert "alice@example.com" in subscribers()
    print("mailer ok:", c)
