"""Microsoft 365 / Google Workspace substitute: docs and sheets."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "office.jsonl"


def new_doc(title: str, kind: str = "doc") -> str:
    did = f"d_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": did, "title": title, "kind": kind,
                            "body": "", "at": time.time()}) + "\n")
    return did


def edit(did: str, body: str) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"id": did, "body": body, "at": time.time()}) + "\n")


if __name__ == "__main__":
    d = new_doc("notes")
    edit(d, "hello")
    print("office ok")
