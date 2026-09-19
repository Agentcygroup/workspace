"""Calendly substitute: time slots and bookings."""
from __future__ import annotations
import json
from pathlib import Path
DB = Path(__file__).resolve().parent / "bookings.jsonl"


def book(slot_iso: str, who: str) -> dict:
    rec = {"slot": slot_iso, "who": who}
    with DB.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def booked() -> list[dict]:
    if not DB.exists():
        return []
    return [json.loads(l) for l in DB.read_text().splitlines() if l.strip()]


if __name__ == "__main__":
    book("2026-10-01T09:00Z", "alice")
    book("2026-10-01T10:00Z", "bob")
    assert len(booked()) >= 2
    print("scheduler ok")
