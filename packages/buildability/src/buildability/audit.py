"""Append-only audit log for classify operations."""
from __future__ import annotations
import json
import subprocess
import time
from pathlib import Path


def log_path(root: Path | None = None) -> Path:
    if root is None:
        root = Path(__file__).resolve().parents[4]
    p = root / "standards" / "classification_log.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def record(spec_name: str, regime: str, path: Path | None = None) -> None:
    p = path or log_path()
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=p.parent.parent, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except Exception:
        commit = "unknown"
    entry = {"spec": spec_name, "regime": regime, "at": time.time(), "commit": commit}
    with p.open("a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def query(regime: str | None = None, since: float | None = None,
          path: Path | None = None) -> list[dict]:
    p = path or log_path()
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if regime and e.get("regime") != regime:
            continue
        if since and e.get("at", 0) < since:
            continue
        out.append(e)
    return out
