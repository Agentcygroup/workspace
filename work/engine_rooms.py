"""Engine rooms: one room per engine declared in work/engines.tsv.

A room is a named engine (a language, a runtime, a framework, a
package manager, a service). Each room has:
  name      the key from the ENGINES map
  command   the toolchain command the map resolves to
  present   whether the first word of the command resolves on PATH
  reachable whether the command itself runs (exit 0) when invoked
  reason    if not present or not reachable, why

Reads work/engines.tsv. Writes work/engine_rooms.json.

Does not install anything. Does not invent engines. Names what exists
and what does not, with the exact command that decided it.
"""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "work" / "engines.tsv"
OUT = ROOT / "work" / "engine_rooms.json"


def first_word(cmd: str) -> str:
    cmd = cmd.strip()
    if cmd.startswith("'") or cmd.startswith('"'):
        quote = cmd[0]
        end = cmd.find(quote, 1)
        if end != -1:
            return cmd[1:end]
    return cmd.split()[0] if cmd.split() else ""


def check(cmd: str) -> tuple[bool, bool, str]:
    fw = first_word(cmd)
    if not fw:
        return False, False, "empty command"
    if shutil.which(fw) is None:
        return False, False, f"not on PATH: {fw}"
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True,
                           text=True, timeout=15)
    except subprocess.TimeoutExpired:
        return True, False, "timeout after 15s"
    except Exception as e:
        return True, False, f"{type(e).__name__}: {e}"
    if r.returncode == 0:
        return True, True, "ok"
    tail = (r.stderr or r.stdout).strip().splitlines()
    return True, False, f"rc={r.returncode}: {tail[-1] if tail else ''}"


def main() -> int:
    if not SOURCE.exists():
        print(f"work/engine_rooms.py: {SOURCE.relative_to(ROOT)} absent.")
        print("run work/engines.sh first, then rerun.")
        return 2

    rows = []
    for line in SOURCE.read_text().splitlines():
        if not line.strip():
            continue
        name, _, cmd = line.partition("\t")
        present, reachable, reason = check(cmd)
        rows.append({
            "name": name,
            "command": cmd,
            "present": present,
            "reachable": reachable,
            "reason": reason,
        })

    total = len(rows)
    present = sum(1 for r in rows if r["present"])
    reachable = sum(1 for r in rows if r["reachable"])

    OUT.write_text(json.dumps({
        "source": str(SOURCE.relative_to(ROOT)),
        "total": total,
        "present": present,
        "reachable": reachable,
        "absent": total - present,
        "rooms": rows,
    }, indent=2) + "\n")

    print(f"total     : {total}")
    print(f"present   : {present}")
    print(f"reachable : {reachable}")
    print(f"absent    : {total - present}")
    print(f"wrote {OUT.relative_to(ROOT)}")

    print("\n--- absent ---")
    for r in rows:
        if not r["present"]:
            print(f"  {r['name']:20} {r['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
