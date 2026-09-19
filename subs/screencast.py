"""Loom substitute: a recorded video reference."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "screencasts.jsonl"


def record(title: str, seconds: float, path: str) -> str:
    sid = f"v_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": sid, "title": title,
                            "seconds": seconds, "path": path,
                            "at": time.time()}) + "\n")
    return sid


if __name__ == "__main__":
    record("demo", 42.0, "/tmp/demo.webm")
    print("screencast ok")
