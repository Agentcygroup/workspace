"""Save the pasted document to work/source.txt, then run the three scripts.

Reads the document from stdin (paste and press Ctrl-D), or from a path
given as the first argument. Writes it to work/source.txt. Then runs:

    work/structure.py
    work/copyleft.py
    work/capabilities.py

Each script refuses if its input is absent or malformed. This file does
not catch those refusals; it lets them print and stops.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work"
TARGET = WORK / "source.txt"

SCRIPTS = [
    "work/structure.py",
    "work/copyleft.py",
    "work/capabilities.py",
]


def main() -> int:
    WORK.mkdir(exist_ok=True)

    if len(sys.argv) > 1 and sys.argv[1] != "-":
        src = Path(sys.argv[1])
        if not src.exists():
            print(f"work/save.py: {src} absent.", file=sys.stderr)
            return 2
        text = src.read_text()
        origin = str(src)
    else:
        if sys.stdin.isatty():
            print("work/save.py: paste the document, then press Ctrl-D.",
                  file=sys.stderr)
        text = sys.stdin.read()
        origin = "stdin"

    if not text.strip():
        print("work/save.py: empty input; nothing to save.", file=sys.stderr)
        return 2

    TARGET.write_text(text)
    print(f"saved {TARGET.relative_to(ROOT)} ({len(text)} bytes) from {origin}")

    for script in SCRIPTS:
        path = ROOT / script
        if not path.exists():
            print(f"skip {script}: absent")
            continue
        print(f"\n=== {script} ===")
        r = subprocess.run([sys.executable, str(path)], cwd=ROOT)
        if r.returncode != 0:
            print(f"{script}: exited {r.returncode}", file=sys.stderr)
            return r.returncode

    print("\nall scripts completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
