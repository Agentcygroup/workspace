"""Pinecone substitute: cosine index over float vectors in SQLite."""
from __future__ import annotations
import math
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "vectors.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS vectors (
  id TEXT PRIMARY KEY,
  dim INTEGER NOT NULL,
  vals TEXT NOT NULL,
  meta TEXT
);
"""


def _conn():
    c = sqlite3.connect(DB)
    c.executescript(SCHEMA)
    return c


def _cos(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def upsert(id_: str, vals: list[float], meta: str = "") -> None:
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO vectors(id, dim, vals, meta) VALUES(?, ?, ?, ?)",
                  (id_, len(vals), ",".join(str(v) for v in vals), meta))


def query(vals: list[float], k: int = 3) -> list[tuple[str, float]]:
    out = []
    with _conn() as c:
        for id_, v, _m in c.execute("SELECT id, vals, meta FROM vectors"):
            vec = [float(x) for x in v.split(",")]
            if len(vec) != len(vals):
                continue
            out.append((id_, _cos(vals, vec)))
    out.sort(key=lambda t: -t[1])
    return out[:k]


if __name__ == "__main__":
    upsert("a", [1.0, 0.0], "east")
    upsert("b", [0.0, 1.0], "north")
    upsert("c", [0.9, 0.1], "east-ish")
    r = query([1.0, 0.0], k=2)
    assert r[0][0] == "a"
    assert r[1][0] == "c"
    print("vec ok:", r)
