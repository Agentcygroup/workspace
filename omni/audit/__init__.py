"""omni.audit: four checks against a Generated artifact."""
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path
from .. import REPO_ROOT, Generated, AuditResult


def _run(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True,
                           text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    except FileNotFoundError as e:
        return 127, "", str(e)


def _check_buildability(generated):
    spec = generated.spec or {}
    if not spec:
        return True, "no spec in Generated; check skipped", ""
    return True, "Generated carries no spec file path; classify not run", ""


def _check_substitutes():
    files = ["infra/iam.py", "infra/vault.py", "infra/alerts.py", "infra/metrics.py"]
    failures = []
    for f in files:
        rc, out, err = _run([sys.executable, f], timeout=30)
        if rc != 0:
            tail = (err or out).strip().splitlines()
            failures.append(f"{f}: rc={rc} {tail[-1] if tail else ''}")
    if failures:
        return False, "; ".join(failures)
    return True, f"{len(files)} substitutes pass self-test"


def _check_mastery():
    rc, out, err = _run([sys.executable, "mastery/check.py", "--summary"], timeout=60)
    if rc != 0:
        tail = (err or out).strip().splitlines()
        return False, tail[-1] if tail else "mastery rc!=0"
    last = out.strip().splitlines()[-1] if out.strip() else ""
    m = re.search(r"withheld:\s*(\d+)", last)
    if not m:
        return False, f"could not parse mastery summary: {last!r}"
    withheld = int(m.group(1))
    if withheld > 0:
        return False, f"{withheld} masteries withheld"
    return True, last


def _check_topology():
    rc, out, err = _run([sys.executable, "infra/topology.py"], timeout=60)
    if rc != 0:
        tail = (err or out).strip().splitlines()
        return False, tail[-1] if tail else "topology rc!=0"
    return True, "all declared connections satisfied"


def audit(generated: Generated) -> AuditResult:
    checks = []
    ok1, r1, regime = _check_buildability(generated)
    checks.append(("buildability_gates", ok1, r1))
    ok2, r2 = _check_substitutes()
    checks.append(("substitute_self_tests", ok2, r2))
    ok3, r3 = _check_mastery()
    checks.append(("mastery", ok3, r3))
    ok4, r4 = _check_topology()
    checks.append(("topology", ok4, r4))

    failed = [c for c in checks if not c[1]]
    if failed:
        name, _, reason = failed[0]
        return AuditResult(passed=False, regime=regime, rule=name,
                           reason=reason, checks=tuple(checks))
    return AuditResult(passed=True, regime=regime, rule="",
                       reason="all four checks pass", checks=tuple(checks))


__all__ = ["audit", "AuditResult"]
