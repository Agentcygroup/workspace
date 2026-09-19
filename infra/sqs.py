"""SQS / Kafka substitute: append-only jsonl queue with ids."""
from __future__ import annotations
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "queues"
ROOT.mkdir(exist_ok=True)


def _q(name: str) -> Path:
    return ROOT / f"{name}.jsonl"


def send(name: str, body: dict) -> str:
    qid = f"{time.time_ns()}"
    with _q(name).open("a") as f:
        f.write(json.dumps({"id": qid, "body": body, "at": time.time()}) + "\n")
    return qid


def receive(name: str, n: int = 10) -> list[dict]:
    p = _q(name)
    if not p.exists():
        return []
    lines = p.read_text().splitlines()
    return [json.loads(l) for l in lines[-n:] if l.strip()]


if __name__ == "__main__":
    send("events", {"kind": "classify", "corpus": "uci"})
    send("events", {"kind": "pipe", "passed": True})
    r = receive("events", 5)
    assert len(r) == 2
    print("sqs ok:", [x["body"]["kind"] for x in r])
