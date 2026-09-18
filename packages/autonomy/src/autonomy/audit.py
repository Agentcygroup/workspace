"""Audit log for autonomy decisions.

Every decision is appended to a JSONL file. The log is a record of what
the system decided and why, and is the input to a reviewer's analysis.
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AuditLog:
    path: Path
    enabled: bool = True

    def append(self, entry: dict) -> None:
        if not self.enabled:
            return
        entry = dict(entry)
        entry["at"] = time.time()
        with self.path.open("a") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")

    def read_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text().splitlines() if line.strip()]
