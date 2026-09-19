"""Nooks substitute: dialer log.

Note: Nooks is a real-time dialing product with telephony rails. This
substitute logs a call; it does not place one.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "dialer.jsonl"


def dialed(number: str, outcome: str = "no_answer") -> dict:
    rec = {"number": number, "outcome": outcome, "at": time.time()}
    with DB.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


if __name__ == "__main__":
    dialed("+15550000001", "connected")
    print("dialer ok")
