"""Index the capabilities named in work/source.txt.

Reads work/source.txt. Produces work/capabilities.json: one row per
capability named in the document, with the section it appears in and
the technology stack the document attributes to it.

A capability is a numbered entry ("1. Name") whose body names a
"Tech:" line or a "Superpower:" line. The document names them in
several sections (initial superpowers, deployable superpowers,
the unified list, the gap-filled list, the gapless list). The index
merges them by name and keeps every section in which the name appears.

Output is a manifest, not a system. It says what the document names,
and where. It does not claim anything runs.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "work" / "source.txt"
OUT = ROOT / "work" / "capabilities.json"

# A capability begins with "N. Name" and ends at the next "N. Name",
# a markdown heading, or the end of file. The body may contain Tech:,
# Superpower:, and Gap Filled: lines.
CAP_START = re.compile(r"^(\d+)\.\s+([A-Z][^\n]{2,120})$")
TECH_LINE = re.compile(r"^\s*[-*]?\s*Tech:\s*(.+)$", re.IGNORECASE)
POWER_LINE = re.compile(r"^\s*[-*]?\s*Superpower:\s*(.+)$", re.IGNORECASE)
GAP_LINE = re.compile(r"^\s*[-*]?\s*Gap Filled:\s*(.+)$", re.IGNORECASE)
HEADING = re.compile(r"^#{1,4}\s+(.+)$|^\*\*(.+?)\*\*\s*$")


def sections_of(lines):
    """Yield (section_title, start_index) for every heading."""
    out = []
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m:
            title = (m.group(1) or m.group(2) or "").strip(": ").strip()
            if title:
                out.append((title, i))
    return out


def section_for(idx: int, sections) -> str:
    last = ""
    for title, start in sections:
        if start <= idx:
            last = title
        else:
            break
    return last


def parse_capabilities(lines):
    caps = []
    sections = sections_of(lines)
    i = 0
    while i < len(lines):
        m = CAP_START.match(lines[i])
        if not m:
            i += 1
            continue
        name = m.group(2).strip()
        section = section_for(i, sections)
        body = []
        j = i + 1
        while j < len(lines):
            if CAP_START.match(lines[j]):
                break
            if HEADING.match(lines[j]):
                break
            body.append(lines[j])
            j += 1
        tech = None
        superpower = None
        gap = None
        for b in body:
            for line, slot in ((TECH_LINE, "tech"), (POWER_LINE, "superpower"),
                               (GAP_LINE, "gap")):
                mm = line.match(b)
                if mm:
                    val = mm.group(1).strip()
                    if slot == "tech" and tech is None:
                        tech = val
                    elif slot == "superpower" and superpower is None:
                        superpower = val
                    elif slot == "gap" and gap is None:
                        gap = val
        caps.append({
            "name": name,
            "section": section,
            "line": i + 1,
            "tech": tech,
            "superpower": superpower,
            "gap_filled": gap,
        })
        i = j
    return caps


def merge(caps):
    """Merge by name. Keep every section where a name appears."""
    by_name = {}
    for c in caps:
        key = c["name"].strip()
        if key not in by_name:
            by_name[key] = {
                "name": key,
                "sections": [c["section"]],
                "lines": [c["line"]],
                "tech": c["tech"],
                "superpower": c["superpower"],
                "gap_filled": c["gap_filled"],
            }
        else:
            row = by_name[key]
            if c["section"] not in row["sections"]:
                row["sections"].append(c["section"])
            row["lines"].append(c["line"])
            row["tech"] = row["tech"] or c["tech"]
            row["superpower"] = row["superpower"] or c["superpower"]
            row["gap_filled"] = row["gap_filled"] or c["gap_filled"]
    return sorted(by_name.values(), key=lambda r: r["lines"][0])


def main() -> int:
    if not SOURCE.exists():
        print(f"work/capabilities.py: {SOURCE.relative_to(ROOT)} absent.")
        print("save the pasted document to that path, then run again.")
        return 2

    lines = SOURCE.read_text().splitlines()
    caps = parse_capabilities(lines)
    merged = merge(caps)

    with_tech = sum(1 for r in merged if r["tech"])
    with_gap = sum(1 for r in merged if r["gap_filled"])

    OUT.write_text(json.dumps({
        "source": str(SOURCE.relative_to(ROOT)),
        "total_unique": len(merged),
        "total_entries": len(caps),
        "with_tech": with_tech,
        "with_gap_filled": with_gap,
        "capabilities": merged,
    }, indent=2) + "\n")

    print(f"unique capabilities : {len(merged)}")
    print(f"total entries       : {len(caps)}")
    print(f"with Tech: line     : {with_tech}")
    print(f"with Gap Filled:    : {with_gap}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
