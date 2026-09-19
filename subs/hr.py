"""Rippling / Workday / Odoo HR substitute: employees and pay runs."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "hr.jsonl"


def hire(name: str, role: str, salary: float) -> str:
    eid = f"emp_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": eid, "name": name, "role": role,
                            "salary": salary, "status": "active",
                            "at": time.time()}) + "\n")
    return eid


def terminate(eid: str) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"id": eid, "status": "terminated",
                            "at": time.time()}) + "\n")


def active() -> list[dict]:
    latest: dict[str, dict] = {}
    if DB.exists():
        for l in DB.read_text().splitlines():
            if not l.strip():
                continue
            e = json.loads(l)
            latest[e["id"]] = {**latest.get(e["id"], {}), **e}
    return [v for v in latest.values() if v.get("status") == "active"]


if __name__ == "__main__":
    e = hire("alice", "engineer", 150000)
    assert any(x["id"] == e for x in active())
    print("hr ok")
