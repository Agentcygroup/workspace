"""HubSpot / Salesforce / EspoCRM substitute: contacts and deals."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "crm.jsonl"


def upsert(kind: str, name: str, fields: dict) -> str:
    rid = f"{kind}_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": rid, "kind": kind, "name": name,
                            "fields": fields, "at": time.time()}) + "\n")
    return rid


def get(kind: str) -> list[dict]:
    if not DB.exists():
        return []
    return [json.loads(l) for l in DB.read_text().splitlines()
            if l.strip() and json.loads(l)["kind"] == kind]


if __name__ == "__main__":
    upsert("contact", "alice", {"org": "acme"})
    upsert("deal", "acme-2026", {"amount": 50000})
    assert len(get("contact")) >= 1
    assert len(get("deal")) >= 1
    print("crm ok")
