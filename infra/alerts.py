"""PagerDuty / Twilio / SendGrid substitute: thresholds over metrics."""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

LOG = Path(__file__).resolve().parent / "alerts.jsonl"


def fire(name: str, reason: str, severity: str = "warn") -> dict:
    rec = {"at": time.time(), "name": name, "reason": reason,
           "severity": severity}
    with LOG.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"[alert:{severity}] {name}: {reason}", file=sys.stderr)
    return rec


def read_all() -> list[dict]:
    if not LOG.exists():
        return []
    return [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]


if __name__ == "__main__":
    fire("queue_depth", "depth > 100", "page")
    assert read_all()[-1]["name"] == "queue_depth"
    print("alerts ok")
