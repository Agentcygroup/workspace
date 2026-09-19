"""Zoom / Jitsi substitute: a meeting record."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "meetings.jsonl"


def schedule(topic: str, start_iso: str, duration_min: int) -> str:
    mid = f"m_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": mid, "topic": topic,
                            "start": start_iso, "duration_min": duration_min,
                            "at": time.time()}) + "\n")
    return mid


if __name__ == "__main__":
    schedule("standup", "2026-10-01T09:00Z", 15)
    print("video ok")
