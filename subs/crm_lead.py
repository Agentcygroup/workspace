"""Apollo / LinkedIn / ZoomInfo substitute: a lead record.

Note: sourcing, networking, and enrichment are data products. This
substitute stores and retrieves a lead; it does not discover one.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "leads.jsonl"


def add(name: str, org: str = "", source: str = "manual") -> str:
    lid = f"lead_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": lid, "name": name, "org": org,
                            "source": source, "at": time.time()}) + "\n")
    return lid


def all_leads() -> list[dict]:
    if not DB.exists():
        return []
    return [json.loads(l) for l in DB.read_text().splitlines() if l.strip()]


if __name__ == "__main__":
    add("alice", org="acme", source="manual")
    assert len(all_leads()) >= 1
    print("crm_lead ok:", len(all_leads()), "leads")
