"""Skill: Continuous Security Audits, wired to the repo's substitutes.

Runs the self-test of each security substitute under infra/ and reports
one row per substitute. Refuses if any self-test exits non-zero, naming
the file and the last line of stderr.

This is the smallest version of the skill from work/pi_agent.json whose
tech stack can be satisfied by files already in the repo. Snyk, Dependabot,
OWASP ZAP, and GitLab CI are not present; the substitutes audit their own
contract (IAM, vault, alerts, metrics) and refuse when the contract fails.
"""
from __future__ import annotations
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBSTITUTES = (
    "infra/iam.py",
    "infra/vault.py",
    "infra/alerts.py",
    "infra/metrics.py",
)


@dataclass(frozen=True)
class AuditRow:
    file: str
    ok: bool
    reason: str


def audit() -> tuple[AuditRow, ...]:
    rows = []
    for rel in SUBSTITUTES:
        p = ROOT / rel
        if not p.exists():
            rows.append(AuditRow(rel, False, "absent"))
            continue
        try:
            r = subprocess.run(
                [sys.executable, str(p)],
                cwd=ROOT, capture_output=True, text=True, timeout=30,
            )
        except subprocess.TimeoutExpired:
            rows.append(AuditRow(rel, False, "timeout"))
            continue
        if r.returncode == 0:
            rows.append(AuditRow(rel, True, "ok"))
        else:
            tail = (r.stderr or r.stdout).strip().splitlines()
            rows.append(AuditRow(rel, False, tail[-1] if tail else f"rc={r.returncode}"))
    return tuple(rows)


def main() -> int:
    rows = audit()
    for r in rows:
        print(f"  {r.file:20} {'ok' if r.ok else 'FAIL':4} {r.reason}")
    fail = sum(1 for r in rows if not r.ok)
    print(f"\n{len(rows)-fail} ok, {fail} fail")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
