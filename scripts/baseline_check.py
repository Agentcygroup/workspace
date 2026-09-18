#!/usr/bin/env python3
"""Assert the current gap report matches the saved baseline.

Treats the baseline as a cache. If absent, creates it and succeeds.
If present, compares and fails on any new unattested claim.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "packages" / "gaps" / "baseline" / "attestation_baseline.json"
GAPS = ROOT / "standards" / "attestation_gaps.json"


def _regenerate_gaps() -> int:
    r = subprocess.run(
        ["python", "packages/gaps/gaps.py"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
    return r.returncode


def _save_baseline() -> int:
    r = subprocess.run(
        ["python", "packages/gaps/gaps.py", "--save-baseline"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
    return r.returncode


def main() -> int:
    if _regenerate_gaps() != 0:
        return 1

    if not BASELINE.exists():
        if _save_baseline() != 0:
            print(f"could not create baseline at {BASELINE}")
            return 2
        print(f"baseline created at {BASELINE}")
        return 0

    base = json.loads(BASELINE.read_text())
    current = json.loads(GAPS.read_text())

    base_ids = set(base.get("unattested_ids", []))
    curr = current.get("unattested", 0)
    if isinstance(curr, list):
        curr_ids = {u["id"] for u in curr}
    else:
        curr_ids = set()

    new_unattested = curr_ids - base_ids
    newly_attested = base_ids - curr_ids

    if new_unattested:
        print(f"regression: {len(new_unattested)} new unattested claims")
        for cid in sorted(new_unattested)[:10]:
            print(f"  {cid}")
        return 1

    if newly_attested:
        print(f"progress: {len(newly_attested)} claims newly attested")

    print(f"baseline stable: {len(curr_ids)} unattested, {len(base_ids)} in baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
