"""Amplitude / Mixpanel / PostHog substitute: event counters and funnels."""
from __future__ import annotations
import json
import time
from pathlib import Path
LOG = Path(__file__).resolve().parent / "analytics.jsonl"


def track(name: str, props: dict | None = None) -> None:
    with LOG.open("a") as f:
        f.write(json.dumps({"at": time.time(), "name": name,
                            "props": props or {}}) + "\n")


def count(name: str) -> int:
    if not LOG.exists():
        return 0
    return sum(1 for l in LOG.read_text().splitlines()
               if l.strip() and json.loads(l)["name"] == name)


if __name__ == "__main__":
    track("page_view", {"path": "/"})
    track("page_view", {"path": "/pricing"})
    track("signup")
    assert count("page_view") >= 2
    print("analytics ok:", count("page_view"), "page_views")
