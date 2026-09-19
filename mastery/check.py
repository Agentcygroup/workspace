"""Walk every mastery file. Refuse if any required artifact is missing.

Reports each mastery by node, its intent, and whether it holds.

  python mastery/check.py           all
  python mastery/check.py --list    names only
  python mastery/check.py --summary counts only
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from mastery import discover
from _schema import check


def main(argv) -> int:
    modes = set(argv)
    masteries = discover()
    ok = 0
    fail = 0
    for name, m in sorted(masteries.items()):
        holds, missing = check(m, ROOT)
        if "--summary" in modes:
            continue
        if "--list" in modes:
            print(f"  {name:12} {'ok' if holds else 'MISSING'}")
            continue
        marker = "ok" if holds else "MISSING"
        print(f"{name:12} [{marker}] {m.intent}")
        if not holds:
            for r in missing:
                print(f"               requires: {r}")
            print(f"               refuses:  {m.refuses}")
        if holds:
            ok += 1
        else:
            fail += 1
    if "--summary" in modes or not modes:
        if "--summary" in modes:
            print(f"masteries: {len(masteries)}  hold: {ok}  withheld: {fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
