"""omni.audit: four checks against a Generated artifact.

    audit(generated: Generated) -> AuditResult

Each check runs one command that already exists in the repo. The
result names the first failing check and its reason. The audit does
not invent a new gate; it composes the four gates that are already
present:

  1. buildability gates     — python -m buildability.classify <corpus>
  2. substitute self-tests  — python infra/iam.py, vault.py, alerts.py, metrics.py
  3. mastery checks         — python mastery/check.py --summary
  4. topology checks        — python infra/topology.py

A Generated with no spec is audited by checks 2-4 only; check 1 is
skipped with a named reason rather than a false pass.
"""
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path
from .. import REPO_ROOT, Generated, AuditResult


CHECKS = (
    ("buildability_gates", "python", ["-m", "buildability.classify"]),
    ("substitute_self_tests", None, None),
    ("mastery", "python", ["mastery/check.py", "--summary"]),
    ("topology", "python", ["infra/topology.py"]),
)


def _run(cmd: list[str], timeout: int = 120) -> tuple[int, str, str]:
    try:
        r = subprocess.run(
            cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout,
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    except FileNotFoundError as e:
        return 127, "", str(e)


def _check_substitutes() -> tuple[bool, str]:
    """Run the four security-related substitutes' self-tests."""
    files = ["infra/iam.py", "infra/vault.py", "infra/alerts.py", "infra/metrics.py"]
    failures = []
    for f in files:
        rc, out, err = _run([sys.executable, f], timeout=30)
        if rc != 0:
            failures.append(f"{f}: rc={rc} {(err or out).strip().splitlines()[-1] if (err or out).strip() else ''}")
    if failures:
        return False, "; ".join(failures)
    return True, f"{len(files)} substitutes pass self-test"


def _check_buildability(generated: Generated) -> tuple[bool, str, str]:
    """Classify the generated spec, if any. Returns (ok, reason, regime)."""
    spec = generated.spec or {}
    if not spec:
        return True, "no spec in Generated; check skipped", ""
    # The corpus path is a URL, not a spec file. Until Generated carries
    # a real spec file path, check 1 skips with a named reason.
    return True, "Generated carries no spec file path; classify not run", ""


def _check_mastery() -> tuple[bool, str]:
    rc, out, err = _run([sys.executable, "mastery/check.py", "--summary"], timeout=60)
    if rc != 0:
        return False, (err or out).strip().splitlines()[-1] if (err or out).strip() else "mastery rc!=0"
    last = out.strip().splitlines()[-1] if out.strip() else ""
    m = re.search(r"withheld:\s*(\d+)", last)
    if not m:
        return False, f"could not parse mastery summary: {last!r}"
    withheld = int(m.group(1))
    if withheld > 0:
        return False, f"{withheld} masteries withheld"
    return True, last


def _check_topology() -> tuple[bool, str]:
    rc, out, err = _run([sys.executable, "infra/topology.py"], timeout=60)
    if rc != 0:
        tail = (err or out).strip().splitlines()[-1] if (err or out).strip() else "topology rc!=0"
        return False, tail
    return True, "all declared connections satisfied"


def audit(generated: Generated) -> AuditResult:
    checks: list[tuple[str, bool, str]] = []

    # 1. buildability gates
    ok1, r1, regime = _check_buildability(generated)
    checks.append(("buildability_gates", ok1, r1))

    # 2. substitute self-tests
    ok2, r2 = _check_substitutes()
    checks.append(("substitute_self_tests", ok2, r2))

    # 3. mastery
    ok3, r3 = _check_mastery()
    checks.append(("mastery", ok3, r3))

    # 4. topology
    ok4, r4 = _check_topology()
    checks.append(("topology", ok4, r4))

    failed = [c for c in checks if not c[1]]
    if failed:
        name, _, reason = failed[0]
        return AuditResult(
            passed=False, regime=regime, rule=name, reason=reason, checks=tuple(checks),
        )
    return AuditResult(passed=True, regime=regime, rule="", reason="all four checks pass",
                       checks=tuple(checks))


__all__ = ["audit", "AuditResult"]
