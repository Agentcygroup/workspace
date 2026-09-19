"""Elasticsearch substitute: inverted index over text files."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = Path(__file__).resolve().parent / "index.json"


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_]+", text.lower())


def build(paths: list[Path]) -> dict:
    idx: dict[str, dict[str, int]] = {}
    for p in paths:
        if not p.exists() or not p.is_file():
            continue
        text = p.read_text(errors="ignore")
        for tok in _tokens(text):
            idx.setdefault(tok, {})
            key = str(p.relative_to(ROOT))
            idx[tok][key] = idx[tok].get(key, 0) + 1
    INDEX.write_text(json.dumps(idx))
    return idx


def load() -> dict:
    if not INDEX.exists():
        return {}
    return json.loads(INDEX.read_text())


def query(term: str) -> list[tuple[str, int]]:
    idx = load()
    hits = idx.get(term.lower(), {})
    return sorted(hits.items(), key=lambda t: -t[1])


if __name__ == "__main__":
    paths = list((ROOT / "specs").glob("*.md")) + list((ROOT / "standards").glob("*.json"))
    idx = build(paths)
    assert "spec" in idx or "invariant" in idx
    hits = query("spec")
    assert hits, "no hits for 'spec'"
    print(f"search ok: {len(idx)} terms, top hits for 'spec': {hits[:3]}")
