"""NetSuite / Odoo / ERPNext substitute: orders, invoices, inventory."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "erp.jsonl"


def post(kind: str, payload: dict) -> str:
    rid = f"{kind}_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": rid, "kind": kind, "payload": payload,
                            "at": time.time()}) + "\n")
    return rid


if __name__ == "__main__":
    o = post("order", {"customer": "acme", "total": 1000})
    post("invoice", {"order": o, "total": 1000})
    print("erp ok:", o)
