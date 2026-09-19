"""Terraform substitute: declare machines, disks, services; apply to JSON."""
from __future__ import annotations
import json
from pathlib import Path

STATE = Path(__file__).resolve().parent / "plan.json"


def machine(name: str, cpu: int, mem_mb: int, disk_gb: int,
            services: list[str]) -> dict:
    return {"kind": "machine", "name": name, "cpu": cpu, "mem_mb": mem_mb,
            "disk_gb": disk_gb, "services": services}


def apply(resources: list[dict]) -> dict:
    state = {"resources": resources, "count": len(resources)}
    STATE.write_text(json.dumps(state, indent=2))
    return state


def read() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {"resources": []}


if __name__ == "__main__":
    r = [machine("node-1", 4, 8192, 100, ["api", "frontend"]),
         machine("node-2", 2, 4096, 50, ["worker"])]
    s = apply(r)
    assert s["count"] == 2
    print("plan ok:", s["count"], "machines")
