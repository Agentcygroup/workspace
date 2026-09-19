"""Contentful + Drupal substitute: content store with schema and roles."""
from __future__ import annotations
import sqlite3
import time
from pathlib import Path

DB = Path(__file__).resolve().parent / "cms.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS content_types (
  name TEXT PRIMARY KEY,
  fields TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL,
  data TEXT NOT NULL,
  created REAL NOT NULL,
  updated REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS users ( name TEXT PRIMARY KEY );
CREATE TABLE IF NOT EXISTS roles ( name TEXT PRIMARY KEY );
CREATE TABLE IF NOT EXISTS grants (
  user TEXT NOT NULL,
  role TEXT NOT NULL,
  PRIMARY KEY (user, role)
);
"""


def _conn():
    c = sqlite3.connect(DB)
    c.executescript(SCHEMA)
    return c


def define_type(name: str, fields: list[str]) -> None:
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO content_types(name, fields) VALUES(?, ?)",
                  (name, ",".join(fields)))


def put(type_: str, data: dict) -> int:
    now = time.time()
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO entries(type, data, created, updated) VALUES(?, ?, ?, ?)",
            (type_, str(data), now, now))
        return cur.lastrowid


def get(entry_id: int) -> dict | None:
    with _conn() as c:
        row = c.execute("SELECT type, data FROM entries WHERE id=?", (entry_id,)).fetchone()
    if not row:
        return None
    return {"id": entry_id, "type": row[0], "data": row[1]}


def list_entries(type_: str | None = None) -> list[dict]:
    with _conn() as c:
        if type_:
            rows = c.execute("SELECT id, type, data FROM entries WHERE type=?", (type_,)).fetchall()
        else:
            rows = c.execute("SELECT id, type, data FROM entries").fetchall()
    return [{"id": r[0], "type": r[1], "data": r[2]} for r in rows]


def grant(user: str, role: str) -> None:
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO users(name) VALUES(?)", (user,))
        c.execute("INSERT OR IGNORE INTO roles(name) VALUES(?)", (role,))
        c.execute("INSERT OR IGNORE INTO grants(user, role) VALUES(?, ?)", (user, role))


def roles_of(user: str) -> list[str]:
    with _conn() as c:
        rows = c.execute("SELECT role FROM grants WHERE user=?", (user,)).fetchall()
    return [r[0] for r in rows]


def has_role(user: str, role: str) -> bool:
    return role in roles_of(user)


if __name__ == "__main__":
    define_type("spec", ["name", "regime"])
    a = put("spec", {"name": "URL-SHORTENER", "regime": "INCOHERENT"})
    b = put("spec", {"name": "UCI-TMS", "regime": "BUILDABLE"})
    assert get(a)["data"].find("URL-SHORTENER") != -1
    assert len(list_entries("spec")) >= 2
    grant("alice", "editor")
    assert has_role("alice", "editor")
    print(f"cms ok: {a}, {b}, roles={roles_of('alice')}")
