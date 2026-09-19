"""Hex / Jupyter substitute: a notebook of cells."""
from __future__ import annotations
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "notebooks.jsonl"


def new(name: str) -> str:
    nid = f"nb_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": nid, "name": name, "cells": []}) + "\n")
    return nid


def add_cell(nid: str, source: str) -> None:
    with DB.open("a") as f:
        f.write(json.dumps({"id": nid, "add_cell": source}) + "\n")


if __name__ == "__main__":
    n = new("analysis")
    add_cell(n, "x = 1 + 1")
    add_cell(n, "print(x)")
    print("notebook ok")
