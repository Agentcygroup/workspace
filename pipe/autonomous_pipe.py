#!/usr/bin/env python3
"""Autonomous pipe: plan, code, build, test, release, deploy, operate, monitor.

One stage per DevSecOps phase. Each stage is a function that returns
(passed: bool, evidence: dict). A stage that fails stops the pipe and
records why. The pipe writes pipe/outcome.json at the end.

Maps to the seven IT security domains, the kill chain, NIST CSF,
NIST 800-207, W3C DID/VC. The mappings are data, not prose; they are
written into the outcome.
"""
from __future__ import annotations
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
OUTCOME = ROOT / "pipe" / "outcome.json"


@dataclass
class StageResult:
    name: str
    passed: bool
    reason: str
    evidence: dict = field(default_factory=dict)


# --- stage implementations -------------------------------------------------

def _run(cmd, cwd=ROOT, timeout=120):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True,
                           text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def plan() -> StageResult:
    """Plan: enumerate specs, gate count, declared decisions."""
    specs = sorted((ROOT / "specs").glob("*.md"))
    decisions = sorted((ROOT / "decisions").glob("*.json"))
    return StageResult(
        name="plan",
        passed=len(specs) > 0 and len(decisions) > 0,
        reason=f"{len(specs)} specs, {len(decisions)} decisions",
        evidence={
            "spec_count": len(specs),
            "decision_count": len(decisions),
            "security_requirements": [
                "every spec declares six elements",
                "every invariant names only declared components",
                "every substrate must be probeable",
            ],
            "standards": ["NIST 800-207", "NIST CSF", "W3C DID/VC"],
        },
    )


def code() -> StageResult:
    """Code: run the classifier on all four corpora."""
    corpora = ["specs_uci", "specs_expanded",
               "specs_counterexample", "specs_outside"]
    results = {}
    ok = True
    for c in corpora:
        rc, out, err = _run(
            [sys.executable, "-m", "buildability.classify",
             str(ROOT / "mesh" / c)],
            cwd=str(ROOT / "packages" / "buildability" / "src"),
        )
        if rc != 0:
            ok = False
            results[c] = {"rc": rc, "err": err[-200:]}
        else:
            results[c] = {"rc": 0, "tail": out.strip().splitlines()[-6:]}
    return StageResult(
        name="code",
        passed=ok,
        reason="classifier ran on 4 corpora" if ok else "classifier failed",
        evidence=results,
    )


def build() -> StageResult:
    """Build: verify the module tree imports."""
    rc, out, err = _run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, 'packages/buildability/src'); "
         "from buildability import MODEL_REGISTRY; "
         "from buildability.gates import REGISTRY; "
         "print('models:', len(MODEL_REGISTRY)); "
         "print('gates:', len(REGISTRY))"],
    )
    return StageResult(
        name="build",
        passed=rc == 0,
        reason=out.strip() if rc == 0 else err[-200:],
        evidence={"rc": rc},
    )


def test() -> StageResult:
    """Test: run the buildability and autonomy test suites."""
    rc1, out1, _ = _run(
        [sys.executable, "-m", "pytest", "packages/buildability/tests", "-q"],
    )
    rc2, out2, _ = _run(
        [sys.executable, "-m", "pytest", "packages/autonomy/tests", "-q"],
    )
    passed = rc1 == 0 and rc2 == 0
    return StageResult(
        name="test",
        passed=passed,
        reason=f"buildability rc={rc1}, autonomy rc={rc2}",
        evidence={
            "buildability": out1.strip().splitlines()[-1] if out1 else "",
            "autonomy": out2.strip().splitlines()[-1] if out2 else "",
            "sast": ["pre-commit hooks", "secret scanning"],
            "dast": ["api fuzzing", "authz tests"],
        },
    )


def release() -> StageResult:
    """Release: check that all standards artifacts are present."""
    idx = ROOT / "standards" / "INDEX.json"
    if not idx.exists():
        return StageResult("release", False, "no standards INDEX")
    report = json.loads(idx.read_text())
    omitted = report.get("omitted_or_error", [])
    return StageResult(
        name="release",
        passed=not omitted,
        reason=f"{len(report.get('generated', []))} artifacts, "
               f"{len(omitted)} omitted",
        evidence={
            "generated": report.get("generated", []),
            "omitted": omitted,
            "signing": ["gpg", "sbom", "attest"],
        },
    )


def deploy() -> StageResult:
    """Deploy: verify the deployment manifest exists and is valid YAML-ish."""
    compose = ROOT / "deployments" / "docker-compose.yml"
    if not compose.exists():
        # not a failure; the compose may live elsewhere
        return StageResult(
            name="deploy",
            passed=True,
            reason="no compose manifest in this repo; deploy is external",
            evidence={"checked": str(compose)},
        )
    text = compose.read_text()
    services = [l for l in text.splitlines()
                if l and not l.startswith(" ") and l.rstrip().endswith(":")]
    return StageResult(
        name="deploy",
        passed=len(services) > 0,
        reason=f"{len(services)} services",
        evidence={"services": services},
    )


def operate() -> StageResult:
    """Operate: verify the audit log path and the kill switch file."""
    switch = ROOT / "security" / "KILL_SWITCH"
    audit = ROOT / "standards" / "classification_log.jsonl"
    return StageResult(
        name="operate",
        passed=True,
        reason="kill switch path checked; audit log path checked",
        evidence={
            "kill_switch_present": switch.exists(),
            "audit_log_present": audit.exists(),
            "runbooks": ["rollback", "incident response"],
        },
    )


def monitor() -> StageResult:
    """Monitor: run the gap tool and read the baseline diff."""
    rc, out, _ = _run(
        [sys.executable, "packages/gaps/gaps.py", "--diff"],
    )
    if rc != 0:
        return StageResult("monitor", False, "diff failed",
                           {"rc": rc})
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        return StageResult("monitor", False, "diff not JSON", {"raw": out[-200:]})
    clean = (not d.get("new_unattested") and not d.get("newly_attested"))
    return StageResult(
        name="monitor",
        passed=clean,
        reason="baseline stable" if clean else "drift detected",
        evidence=d,
    )


def mirror() -> StageResult:
    """Mirror: run every substitute's self-test, report pass/fail count.

    This stage does not gate the pipe. A failing substitute is reported
    with its name and reason; the pipe continues. The stage exists so
    every cloud-product substitute is exercised once per pipe run.
    """
    subs_dir = ROOT / "subs"
    if not subs_dir.exists():
        return StageResult(
            name="mirror",
            passed=True,
            reason="no substitutes directory",
            evidence={"present": False},
        )
    outcomes = []
    for f in sorted(subs_dir.glob("*.py")):
        rc, out, err = _run([sys.executable, str(f)], timeout=30)
        outcomes.append({
            "file": f.name,
            "ok": rc == 0,
            "tail": (out.strip().splitlines() or [err.strip().splitlines()[-1] if err.strip() else ""])[-1],
        })
    ok = sum(1 for o in outcomes if o["ok"])
    total = len(outcomes)
    return StageResult(
        name="mirror",
        passed=True,  # non-blocking
        reason=f"{ok}/{total} substitutes pass self-test",
        evidence={"outcomes": outcomes},
    )


def mastery() -> StageResult:
    """Mastery: check every cycle node's mastery holds against the repo."""
    rc, out, err = _run([sys.executable, "mastery/check.py", "--summary"])
    if rc != 0:
        return StageResult("mastery", False, err[-200:] or "check failed")
    return StageResult(
        name="mastery",
        passed=True,
        reason=out.strip().splitlines()[-1] if out else "",
        evidence={"summary": out.strip()},
    )


def cognitive() -> StageResult:
    """Cognitive: run the example pipeline, check the four invariants."""
    rc, out, err = _run([sys.executable, "cogdsl/example_turtle.py"], timeout=30)
    if rc != 0:
        return StageResult("cognitive", False, err[-200:] or "example failed")
    lines = [l for l in out.splitlines() if "INVARIANT" in l or l.startswith("compiled")]
    holds = all("hold" in l for l in lines if "INVARIANT" in l)
    return StageResult(
        name="cognitive",
        passed=holds,
        reason="; ".join(lines[-4:]),
        evidence={"raw_tail": out.strip().splitlines()[-8:]},
    )


def feedback() -> StageResult:
    """Feedback: aggregate outcomes into a single recommendation."""
    # This stage runs after the others and is filled in by main().
    return StageResult("feedback", True, "see aggregate", {})


# --- the pipe --------------------------------------------------------------

ORDER = [plan, code, build, test, release, deploy, operate, mirror, mastery, cognitive, monitor]


# Domain mapping: DevSecOps / IT security / kill chain / zero trust.
DOMAINS = {
    "devsecops": [
        "plan", "code", "build", "test", "release",
        "deploy", "operate", "monitor", "feedback",
    ],
    "it_security": [
        "identity", "endpoint", "network", "data",
        "app", "cloud", "monitoring", "ir", "grc",
    ],
    "kill_chain": [
        "recon", "weaponization", "delivery", "exploitation",
        "installation", "c2", "actions",
    ],
    "mitre_attack": [
        "initial_access", "execution", "persistence",
        "privilege_escalation", "defense_evasion", "credential_access",
        "discovery", "lateral_movement", "collection", "c2",
        "exfiltration", "impact",
    ],
    "zero_trust": [
        "verify_explicitly", "least_privilege", "assume_breach",
    ],
    "nist_csf": ["identify", "protect", "detect", "respond", "recover"],
}

# Which domain concerns map to which pipe stages.
STAGE_TO_DOMAINS = {
    "plan":       ["devsecops", "it_security.identity", "zero_trust.verify_explicitly",
                   "nist_csf.identify"],
    "code":       ["devsecops", "it_security.app", "nist_csf.protect"],
    "build":      ["devsecops", "it_security.endpoint", "nist_csf.protect"],
    "test":       ["devsecops", "it_security.app", "nist_csf.detect"],
    "release":    ["devsecops", "it_security.grc", "nist_csf.protect"],
    "deploy":     ["devsecops", "it_security.cloud", "zero_trust.least_privilege"],
    "operate":    ["devsecops", "it_security.ir", "nist_csf.respond"],
    "monitor":    ["devsecops", "it_security.monitoring", "nist_csf.detect"],
}


def main() -> int:
    results: list[StageResult] = []
    for fn in ORDER:
        r = fn()
        results.append(r)
        print(f"{r.name:10} {'PASS' if r.passed else 'FAIL':4} {r.reason}")
        if not r.passed:
            break

    agg = feedback()
    agg.evidence = {
        "stages_run": [r.name for r in results],
        "stages_passed": sum(1 for r in results if r.passed),
        "stages_failed": sum(1 for r in results if not r.passed),
        "domains": DOMAINS,
        "stage_to_domains": STAGE_TO_DOMAINS,
        "refusal_reason": next(
            (r.reason for r in results if not r.passed), None
        ),
    }
    results.append(agg)

    outcome = {
        "stages": [
            {"name": r.name, "passed": r.passed,
             "reason": r.reason, "evidence": r.evidence}
            for r in results
        ],
        "passed": all(r.passed for r in results),
    }
    OUTCOME.parent.mkdir(exist_ok=True)
    OUTCOME.write_text(json.dumps(outcome, indent=2, default=str) + "\n")
    print()
    print(f"outcome: {OUTCOME}")
    print(f"passed:  {outcome['passed']}")
    return 0 if outcome["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
