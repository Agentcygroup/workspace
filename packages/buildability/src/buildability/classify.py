"""Classify every spec in a directory. Prints a table + distribution."""
from __future__ import annotations
import argparse, sys
from collections import Counter
from pathlib import Path
from .loader import spec_from_file
from .procedure import evaluate
from .intent import IntentRatio


def classify_dir(d: Path, gap_history: list[int] | None = None) -> dict:
    rows, dist = [], Counter()
    for p in sorted(Path(d).glob("*.json")):
        if p.name.startswith("_"):
            continue
        spec = spec_from_file(p)
        v = evaluate(spec, gap_history=gap_history)
        regime = v.regime if isinstance(v.regime, str) else v.regime.value
        ratio = IntentRatio.measure(spec, gap_history or [])
        rows.append((p.stem, regime, ratio.closed()))
        dist[regime] += 1
    return {"rows": rows, "distribution": dict(dist)}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="buildability-classify")
    ap.add_argument("dir", type=Path)
    ap.add_argument("--gap-history", type=int, nargs="*", default=None)
    args = ap.parse_args(argv)

    result = classify_dir(args.dir, args.gap_history)
    width = max((len(n) for n, *_ in result["rows"]), default=0)
    for name, regime, closed in result["rows"]:
        flag = "C" if closed else " "
        print(f"{name:<{width}}  {regime:<14} [{flag}]")
    print()
    print("distribution:")
    for regime, n in sorted(result["distribution"].items()):
        print(f"  {regime:<14} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
