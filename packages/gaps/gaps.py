"""CLI: python packages/gaps/gaps.py [--summary] [--list] [--save-baseline] [--diff]"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))

from gaps import (
    collect_claims, attest_all, write_gap_report,
    save_baseline, diff_baseline,
)

ROOT = HERE.parent.parent


def main(argv=None):
    argv = argv or sys.argv[1:]
    claims = collect_claims(ROOT)
    claims = attest_all(ROOT, claims)
    report = write_gap_report(ROOT, claims)

    if "--save-baseline" in argv:
        p = save_baseline(ROOT, claims)
        print(f"baseline saved to {p}")
        return 0

    if "--diff" in argv:
        d = diff_baseline(ROOT, claims)
        print(json.dumps(d, indent=2))
        return 0

    print(f"total claims:  {report['total_claims']}")
    print(f"attested:      {report['attested']}")
    print(f"unattested:    {report['unattested']}")
    print()
    print("by kind:")
    for k, n in sorted(report["by_kind"].items()):
        print(f"  {k:12} {n}")
    print()
    if report["unattested_by_kind"]:
        print("unattested by kind:")
        for k, n in sorted(report["unattested_by_kind"].items()):
            print(f"  {k:12} {n}")

    if "--list" in argv:
        print()
        print("unattested claims:")
        for u in report["unattested"]:
            print(f"  [{u['kind']:12}] {u['id']}")
            print(f"    text: {u['text']}")
            print(f"    need: {u['evidence_needed']}")
            print(f"    why:  {u['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
