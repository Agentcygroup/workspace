#!/usr/bin/env python3
"""Verify no two packages claim the same top-level Python module name."""
from __future__ import annotations
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    claims = defaultdict(list)
    for pkg in (ROOT / "packages").iterdir():
        src = pkg / "src"
        if src.is_dir():
            for mod in src.iterdir():
                if mod.is_dir() and (mod / "__init__.py").exists():
                    claims[mod.name].append(mod)
        for mod in pkg.iterdir():
            if mod.is_dir() and mod.name != "src" and (mod / "__init__.py").exists():
                claims[mod.name].append(mod)

    conflicts = {k: v for k, v in claims.items() if len(v) > 1}
    if conflicts:
        for name, paths in conflicts.items():
            print(f"conflict: {name}")
            for path in paths:
                print(f"  {path}")
        return 1
    print(f"namespace ok: {len(claims)} distinct top-level names")
    return 0


if __name__ == "__main__":
    sys.exit(main())
