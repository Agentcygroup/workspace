"""Stripe substitute: payments ledger.

Note: Stripe is a payment rail that moves money through card networks
and banks. This substitute records a charge; it does not move money.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "payments.jsonl"


def charge(customer: str, amount_cents: int, currency: str = "usd") -> str:
    pid = f"ch_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": pid, "customer": customer,
                            "amount_cents": amount_cents, "currency": currency,
                            "status": "recorded", "at": time.time()}) + "\n")
    return pid


if __name__ == "__main__":
    c = charge("acme", 5000)
    print("payments ok:", c)
