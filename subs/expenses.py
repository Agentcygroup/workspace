"""Ramp substitute: expense records.

Note: Ramp issues cards and clears transactions through a bank. This
substitute records an expense; it does not clear one.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "expenses.jsonl"


def submit(employee: str, amount: float, category: str) -> str:
    eid = f"x_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": eid, "employee": employee,
                            "amount": amount, "category": category,
                            "status": "submitted", "at": time.time()}) + "\n")
    return eid


def approve(eid: str) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"id": eid, "status": "approved",
                            "at": time.time()}) + "\n")


if __name__ == "__main__":
    e = submit("alice", 42.0, "travel")
    approve(e)
    print("expenses ok:", e)
