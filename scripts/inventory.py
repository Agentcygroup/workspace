#!/usr/bin/env python3
"""Map every spec to the code that satisfies it, or note it as unimplemented.

Each spec file in specs/ has a "Current state" section. This script
checks whether the artifact described actually exists by looking for a
declared marker in the spec file itself:

    state: done       -> artifact exists and is tested
    state: partial    -> artifact partially exists
    state: not-done   -> artifact does not exist

The script validates internal consistency (a spec marked done must
declare an evidence file that exists) and prints a summary.

Usage:
    python scripts/inventory.py           # print summary
    python scripts/inventory.py --check   # exit non-zero on inconsistency
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "specs"

STATE_RE = re.compile(r"^state:\s*(done|partial|not-done)\s*$", re.MULTILINE)
EVIDENCE_RE = re.compile(r"^evidence-file:\s*(.+?)\s*$", re.MULTILINE)


def parse_spec(path: Path) -> dict:
    text = path.read_text()
    state_match = STATE_RE.search(text)
    evidence_match = EVIDENCE_RE.search(text)
    return {
        "path": path.name,
        "state": state_match.group(1) if state_match else "unknown",
        "evidence_file": evidence_match.group(1) if evidence_match else None,
    }


def main(argv: list[str]) -> int:
    check = "--check" in argv
    if not SPECS.exists():
        print(f"no specs directory at {SPECS}")
        return 1

    entries = []
    for p in sorted(SPECS.glob("*.md")):
        entries.append(parse_spec(p))

    by_state = {}
    for e in entries:
        by_state.setdefault(e["state"], []).append(e)

    print(f"specs: {len(entries)}")
    for state in ("done", "partial", "not-done", "unknown"):
        items = by_state.get(state, [])
        if items:
            print(f"  {state:10} {len(items)}")

    if not check:
        return 0

    # In check mode, verify internal consistency.
    problems = []
    for e in entries:
        if e["state"] == "unknown":
            problems.append(f"{e['path']}: missing 'state:' line")
            continue
        if e["state"] == "done":
            if not e["evidence_file"]:
                problems.append(f"{e['path']}: state=done but no 'evidence-file:'")
                continue
            target = ROOT / e["evidence_file"]
            if not target.exists():
                problems.append(f"{e['path']}: evidence-file {e['evidence_file']} not found")

    if problems:
        print(f"inconsistencies: {len(problems)}")
        for p in problems:
            print(f"  {p}")
        return 1

    print("inventory consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
