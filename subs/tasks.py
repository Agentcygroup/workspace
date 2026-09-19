"""ClickUp / monday.com / Trello substitute: a board of tasks."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "tasks.jsonl"
COLUMNS = ["todo", "doing", "done"]


def add(title: str, column: str = "todo") -> str:
    assert column in COLUMNS
    tid = f"t_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": tid, "title": title, "col": column,
                            "at": time.time()}) + "\n")
    return tid


def move(tid: str, column: str) -> None:
    assert column in COLUMNS
    with DB.open("a") as f:
        f.write(json.dumps({"id": tid, "col": column, "at": time.time()}) + "\n")


def board() -> dict[str, list[dict]]:
    latest: dict[str, dict] = {}
    if DB.exists():
        for l in DB.read_text().splitlines():
            if not l.strip():
                continue
            e = json.loads(l)
            latest[e["id"]] = {**latest.get(e["id"], {}), **e}
    out = {c: [] for c in COLUMNS}
    for v in latest.values():
        if "col" in v:
            out[v["col"]].append(v)
    return out


if __name__ == "__main__":
    t = add("ship")
    move(t, "doing")
    assert any(x["id"] == t for x in board()["doing"])
    print("tasks ok")
