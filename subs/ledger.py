"""QuickBooks / GnuCash substitute: double-entry ledger."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "ledger.jsonl"


def post(debit: str, credit: str, amount: float, memo: str = "") -> str:
    assert amount >= 0
    eid = f"e_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": eid, "debit": debit, "credit": credit,
                            "amount": amount, "memo": memo,
                            "at": time.time()}) + "\n")
    return eid


def balance(account: str) -> float:
    if not DB.exists():
        return 0.0
    total = 0.0
    for l in DB.read_text().splitlines():
        if not l.strip():
            continue
        e = json.loads(l)
        if e["debit"] == account:
            total += e["amount"]
        if e["credit"] == account:
            total -= e["amount"]
    return total


if __name__ == "__main__":
    post("cash", "revenue", 100.0, "first sale")
    post("cash", "revenue", 50.0, "second sale")
    assert balance("cash") == 150.0
    print("ledger ok: cash =", balance("cash"))
