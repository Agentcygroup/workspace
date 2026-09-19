"""Prometheus / Datadog substitute: counters and gauges to jsonl."""
from __future__ import annotations
import json
import time
from pathlib import Path

LOG = Path(__file__).resolve().parent / "metrics.jsonl"
_counters: dict[str, float] = {}
_gauges: dict[str, float] = {}


def inc(name: str, by: float = 1.0, labels: dict | None = None) -> None:
    _counters[name] = _counters.get(name, 0.0) + by
    _emit("counter", name, _counters[name], labels or {})


def gauge(name: str, value: float, labels: dict | None = None) -> None:
    _gauges[name] = value
    _emit("gauge", name, value, labels or {})


def _emit(kind: str, name: str, value: float, labels: dict) -> None:
    with LOG.open("a") as f:
        f.write(json.dumps({"at": time.time(), "kind": kind,
                            "name": name, "value": value,
                            "labels": labels}) + "\n")


def read_all() -> list[dict]:
    if not LOG.exists():
        return []
    return [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]


if __name__ == "__main__":
    inc("requests", 1, {"path": "/api/health"})
    gauge("queue_depth", 3)
    entries = read_all()
    assert len(entries) >= 2
    print("metrics ok:", [e["name"] for e in entries])
