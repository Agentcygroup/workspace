"""Ashby / Greenhouse substitute: applicant tracking."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "applicants.jsonl"
STAGES = ["applied", "screen", "interview", "offer", "hired", "rejected"]


def apply(name: str, role: str) -> str:
    aid = f"app_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": aid, "name": name, "role": role,
                            "stage": "applied", "at": time.time()}) + "\n")
    return aid


def advance(aid: str, stage: str) -> None:
    assert stage in STAGES, f"unknown stage {stage}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": aid, "stage": stage,
                            "at": time.time()}) + "\n")


def by_stage(stage: str) -> list[dict]:
    if not DB.exists():
        return []
    latest: dict[str, dict] = {}
    for l in DB.read_text().splitlines():
        if not l.strip():
            continue
        e = json.loads(l)
        latest[e["id"]] = {**latest.get(e["id"], {}), **e}
    return [v for v in latest.values() if v.get("stage") == stage]


if __name__ == "__main__":
    a = apply("alice", "engineer")
    advance(a, "interview")
    assert any(x["id"] == a for x in by_stage("interview"))
    print("ats ok")
