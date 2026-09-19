"""Outreach / Salesloft substitute: cadence steps.

Note: Outreach and Salesloft are multi-channel engagement products.
This substitute records steps; it does not send them.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "sequences.jsonl"


def cadence(name: str, steps: list[str]) -> str:
    cid = f"seq_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": cid, "name": name, "steps": steps,
                            "at": time.time()}) + "\n")
    return cid


if __name__ == "__main__":
    c = cadence("q4-outreach", ["email", "call", "email"])
    print("sequences ok:", c)
