"""Tableau / Metabase / Superset substitute: named queries over lakehouse."""
from __future__ import annotations
import json
import time
from pathlib import Path
from . import lakehouse as lh
DB = Path(__file__).resolve().parent / "bi.jsonl"


def save(name: str, table: str, where: dict) -> str:
    qid = f"q_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": qid, "name": name,
                            "table": table, "where": where,
                            "at": time.time()}) + "\n")
    return qid


def run(qid: str) -> list[dict]:
    if not DB.exists():
        return []
    for l in DB.read_text().splitlines():
        if not l.strip():
            continue
        e = json.loads(l)
        if e["id"] == qid:
            return lh.query(e["table"], e["where"])
    return []


if __name__ == "__main__":
    lh.insert("bi_test", {"x": 1})
    lh.insert("bi_test", {"x": 2})
    q = save("x is 1", "bi_test", {"x": 1})
    assert len(run(q)) == 1
    print("bi ok")
