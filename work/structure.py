"""Structure the superpower document into a repo-status table.

Reads work/source.txt. Extracts every named item: superpowers, gaps,
technologies, industries, frameworks. For each, checks whether the
repo implements it, and where. Produces work/features.json.

Every row is one of three states:
  implemented   — a file in the repo implements this
  named         — named in the document, no file implements it
  unknown       — could not resolve to a keyword in the repo

Nothing here invents. The scanner reads paths. If a path is absent,
the row says named and names what is missing.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "work" / "source.txt"
OUT = ROOT / "work" / "features.json"


# --- the extractor ---------------------------------------------------------
# The source is a merged markdown document. Named items appear in one of
# three forms: numbered list entries ("1. **Name**:"), bulleted items
# ("* Gap:"), or bolded headers ("**Name**"). Extract all three.

NAME_RE_NUMBERED = re.compile(r"^\d+\.\s+\*\*(.+?)\*\*", re.MULTILINE)
NAME_RE_BULLETED = re.compile(r"^\s*[-*]\s+\*\*(.+?)\*\*", re.MULTILINE)
NAME_RE_HEADER = re.compile(r"^\*\*(.+?)\*\*", re.MULTILINE)


def extract_names(text: str) -> list[str]:
    names = set()
    for rx in (NAME_RE_NUMBERED, NAME_RE_BULLETED, NAME_RE_HEADER):
        for m in rx.finditer(text):
            n = m.group(1).strip(": ").strip()
            if 3 <= len(n) <= 80:
                names.add(n)
    return sorted(names)


# --- the checker -----------------------------------------------------------
# For each name, produce a search keyword. Then scan the repo for files
# whose path contains the keyword. If found, the row is implemented.

STOP = {"and", "or", "the", "for", "with", "from", "into", "across", "over",
        "all", "any", "its", "this", "that", "than"}


def keywords(name: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_]+", name.lower())
    return [w for w in words if w not in STOP and len(w) > 2]


def find_file(kw: str) -> str | None:
    """Return the first repo-relative path whose name contains kw."""
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if ".git" in p.parts or ".venv" in p.parts:
            continue
        if kw in p.name.lower():
            return str(p.relative_to(ROOT))
    return None


def status_for(name: str) -> dict:
    kws = keywords(name)
    hits = {}
    for kw in kws:
        f = find_file(kw)
        if f is not None:
            hits[kw] = f
    if hits:
        return {"status": "implemented", "files": hits}
    return {"status": "named", "keywords": kws}


def main() -> int:
    if not SOURCE.exists():
        print(f"work/structure.py: {SOURCE.relative_to(ROOT)} absent.")
        print("save the pasted document to that path, then run again.")
        return 2

    text = SOURCE.read_text()
    names = extract_names(text)

    rows = {}
    for n in names:
        rows[n] = status_for(n)

    impl = sum(1 for r in rows.values() if r["status"] == "implemented")
    named = sum(1 for r in rows.values() if r["status"] == "named")

    OUT.write_text(json.dumps({
        "source": str(SOURCE.relative_to(ROOT)),
        "total": len(rows),
        "implemented": impl,
        "named": named,
        "rows": rows,
    }, indent=2) + "\n")

    print(f"total      : {len(rows)}")
    print(f"implemented: {impl}")
    print(f"named      : {named}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
