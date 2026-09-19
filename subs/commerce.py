"""Shopify / Saleor / Medusa substitute: catalog and orders."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "commerce.jsonl"


def product(sku: str, name: str, price: float) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"op": "product", "sku": sku, "name": name,
                            "price": price, "at": time.time()}) + "\n")


def order(sku: str, qty: int) -> str:
    oid = f"o_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"op": "order", "id": oid, "sku": sku,
                            "qty": qty, "at": time.time()}) + "\n")
    return oid


if __name__ == "__main__":
    product("sku-1", "widget", 9.99)
    o = order("sku-1", 2)
    print("commerce ok:", o)
