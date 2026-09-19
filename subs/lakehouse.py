"""Databricks / Snowflake substitute: append-only columnar-ish table."""
from __future__ import annotations
import json
from pathlib import Path
DB = Path(__file__).resolve().parent / "lakehouse.jsonl"


def insert(table: str, row: dict) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"table": table, "row": row}) + "\n")


def scan(table: str) -> list[dict]:
    if not DB.exists():
        return []
    return [json.loads(l)["row"] for l in DB.read_text().splitlines()
            if l.strip() and json.loads(l).get("table") == table]


def query(table: str, where: dict) -> list[dict]:
    return [r for r in scan(table)
            if all(r.get(k) == v for k, v in where.items())]


if __name__ == "__main__":
    insert("sales", {"id": 1, "amount": 100, "region": "eu"})
    insert("sales", {"id": 2, "amount": 200, "region": "us"})
    assert len(query("sales", {"region": "eu"})) == 1
    print("lakehouse ok")
