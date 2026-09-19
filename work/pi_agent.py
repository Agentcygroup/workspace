"""Parse a superpower document into a pi-dev agent skills manifest.

Reads work/source.txt (or a path given as argv[1]). Produces
work/pi_agent.json:

    {
      "skills": [
        {
          "name": "...",
          "kind": "skill",              # a verb an agent can perform
          "section": "...",             # where it appears in the source
          "line": N,
          "tech": "...",                # the stack the source names
          "superpower": "...",          # one-line behavior claim
          "gap_filled": "..."           # what the source says was missing
        },
        ...
      ],
      "capabilities": [ ... ]           # same rows, sorted by name
    }

A "skill" is an entry whose name is a verb phrase ("Automated Code
Review Bot", "Zero-Config Deployment Pipeline", "Dorking").
A "capability" is an entry whose name is a noun phrase ("Self-Healing
Infrastructure", "Real-Time Collaboration", "Version Control").

Both forms appear in the source. The parser names them and attaches
whatever Tech:/Superpower:/Gap Filled: lines follow.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "work" / "source.txt"
OUT = ROOT / "work" / "pi_agent.json"

CAP_START = re.compile(r"^(\d+)\.\s+([A-Z][^\n]{2,120})$")
TECH_LINE = re.compile(r"^\s*[-*]?\s*Tech(?:\s+Stack)?:\s*(.+)$", re.IGNORECASE)
POWER_LINE = re.compile(r"^\s*[-*]?\s*Superpower:\s*(.+)$", re.IGNORECASE)
GAP_LINE = re.compile(r"^\s*[-*]?\s*Gap Filled:\s*(.+)$", re.IGNORECASE)
HEADING = re.compile(r"^#{1,4}\s+(.+)$|^\*\*(.+?)\*\*\s*$")

# Verbs that mark a name as a skill (an action an agent performs).
VERB_HINTS = (
    "auto", "build", "check", "code", "compute", "control", "create",
    "debug", "deploy", "detect", "generate", "index", "ingest",
    "integrate", "orchestrate", "parse", "predict", "review", "route",
    "run", "scan", "schedule", "select", "sync", "test", "track",
    "translate", "update", "verify", "watch", "write",
)

# Nouns that mark a name as a capability (a property an agent has).
NOUN_HINTS = (
    "assistance", "capability", "collaboration", "compatibility",
    "completion", "control", "environment", "infrastructure", "insight",
    "integration", "intelligence", "management", "monitoring",
    "optimization", "pipeline", "sync", "telemetry", "testing",
    "version", "vision",
)


def sections_of(lines):
    out = []
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m:
            title = (m.group(1) or m.group(2) or "").strip(": ").strip()
            if title:
                out.append((title, i))
    return out


def section_for(idx, sections):
    last = ""
    for title, start in sections:
        if start <= idx:
            last = title
        else:
            break
    return last


def classify(name: str) -> str:
    low = name.lower()
    for v in VERB_HINTS:
        if v in low.split() or low.startswith(v + " ") or (" " + v + " ") in low:
            return "skill"
    for n in NOUN_HINTS:
        if n in low:
            return "capability"
    # Default: a name with a gerund or verb-ending is a skill.
    if low.endswith(("ing", "ate", "ify", "ize")):
        return "skill"
    return "capability"


def parse(lines):
    rows = []
    sections = sections_of(lines)
    i = 0
    while i < len(lines):
        m = CAP_START.match(lines[i])
        if not m:
            i += 1
            continue
        name = m.group(2).strip()
        body = []
        j = i + 1
        while j < len(lines):
            if CAP_START.match(lines[j]) or HEADING.match(lines[j]):
                break
            body.append(lines[j])
            j += 1
        tech = sp = gap = None
        for b in body:
            for rx, slot in ((TECH_LINE, "tech"), (POWER_LINE, "sp"),
                             (GAP_LINE, "gap")):
                mm = rx.match(b)
                if mm:
                    val = mm.group(1).strip()
                    if slot == "tech" and tech is None:
                        tech = val
                    elif slot == "sp" and sp is None:
                        sp = val
                    elif slot == "gap" and gap is None:
                        gap = val
        rows.append({
            "name": name,
            "kind": classify(name),
            "section": section_for(i, sections),
            "line": i + 1,
            "tech": tech,
            "superpower": sp,
            "gap_filled": gap,
        })
        i = j
    return rows


def merge(rows):
    by_name = {}
    for r in rows:
        key = r["name"].strip()
        if key not in by_name:
            by_name[key] = dict(r, sections=[r["section"]], lines=[r["line"]])
        else:
            row = by_name[key]
            if r["section"] not in row["sections"]:
                row["sections"].append(r["section"])
            row["lines"].append(r["line"])
            row["tech"] = row["tech"] or r["tech"]
            row["superpower"] = row["superpower"] or r["superpower"]
            row["gap_filled"] = row["gap_filled"] or r["gap_filled"]
    # Drop the single-section fields now that sections/lines carry it.
    out = []
    for r in by_name.values():
        r.pop("section", None)
        r.pop("line", None)
        out.append(r)
    return sorted(out, key=lambda r: r["lines"][0])


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    if not path.exists():
        print(f"work/pi_agent.py: {path} absent.")
        print("save the pasted document there, or pass a path as argv[1].")
        return 2

    lines = path.read_text().splitlines()
    rows = merge(parse(lines))

    skills = [r for r in rows if r["kind"] == "skill"]
    caps = [r for r in rows if r["kind"] == "capability"]

    OUT.write_text(json.dumps({
        "source": str(path),
        "total": len(rows),
        "skills": len(skills),
        "capabilities": len(caps),
        "with_tech": sum(1 for r in rows if r["tech"]),
        "with_superpower": sum(1 for r in rows if r["superpower"]),
        "with_gap_filled": sum(1 for r in rows if r["gap_filled"]),
        "rows": rows,
    }, indent=2) + "\n")

    print(f"total        : {len(rows)}")
    print(f"skills       : {len(skills)}")
    print(f"capabilities : {len(caps)}")
    print(f"with Tech    : {sum(1 for r in rows if r['tech'])}")
    print(f"with Superpwr: {sum(1 for r in rows if r['superpower'])}")
    print(f"with GapFill : {sum(1 for r in rows if r['gap_filled'])}")
    print(f"wrote {OUT.relative_to(ROOT)}")

    print("\n--- skills (first 20) ---")
    for r in skills[:20]:
        print(f"  {r['name']}")
    print("\n--- capabilities (first 20) ---")
    for r in caps[:20]:
        print(f"  {r['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
