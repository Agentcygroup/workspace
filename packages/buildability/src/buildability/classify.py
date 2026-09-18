"""Classify every spec in a directory. Prints a table + distribution."""
from __future__ import annotations
import argparse, sys
from collections import Counter
from pathlib import Path
from .loader import spec_from_file
from .procedure import evaluate


def classify_dir(d: Path, gap_history: list[int] | None = None) -> dict:
    rows, dist = [], Counter()
    for p in sorted(Path(d).glob("*.json")):
        if p.name.startswith("_"):
            continue
        v = evaluate(spec_from_file(p), gap_history=gap_history)
        regime = v.regime if isinstance(v.regime, str) else v.regime.value
        rows.append((p.stem, regime))
        dist[regime] += 1
    return {"rows": rows, "distribution": dict(dist)}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="buildability-classify")
    ap.add_argument("dir", type=Path)
    ap.add_argument("--gap-history", type=int, nargs="*", default=None)
    args = ap.parse_args(argv)

    result = classify_dir(args.dir, args.gap_history)
    width = max((len(n) for n, _ in result["rows"]), default=0)
    for name, regime in result["rows"]:
        print(f"{name:<{width}}  {regime}")
    print()
    print("distribution:")
    for regime, n in sorted(result["distribution"].items()):
        print(f"  {regime:<14} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
