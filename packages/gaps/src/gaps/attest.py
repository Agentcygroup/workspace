"""Attest each claim. Rewire every positive claim to a re-runnable check."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
from .claims import Claim


def _run(cmd, cwd, timeout=60):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True,
                           text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)


def _attest_test(root, c):
    """Mark a single test claim. Actual pytest runs are batched.

    This function is called once per claim during enumeration, but the
    actual work is deferred: attest_all() collects all test claims and
    runs pytest once. See _attest_tests_batch below.
    """
    # Nothing to do here; the batch runs after enumeration.
    pass


def _attest_tests_batch(root, test_claims):
    """Run pytest once for all test claims and mark each result.

    Groups claims by source file, runs pytest once per file, parses
    the summary line to find which tests passed.
    """
    from collections import defaultdict
    by_file = defaultdict(list)
    for c in test_claims:
        name = c.id.split("test:", 1)[1] if "test:" in c.id else c.id
        by_file[c.source].append((c, name))

    for source, items in by_file.items():
        target = root / source
        if not target.exists():
            for c, _ in items:
                c.evidence_found = False
                c.evidence_where = f"source file missing: {source}"
            continue
        # Run pytest once for the whole file, verbose so we can parse names.
        code, out, err = _run(
            ["python", "-m", "pytest", "-v", "--no-header",
             str(target)],
            root, timeout=120,
        )
        # Parse lines like:
        #   path::test_name PASSED
        #   path::test_name FAILED
        passed = set()
        failed = set()
        for line in out.splitlines():
            if " PASSED" in line:
                # extract test name after the last ::
                if "::" in line:
                    name = line.split("::", 1)[1].split()[0]
                    passed.add(name)
            elif " FAILED" in line or " ERROR" in line:
                if "::" in line:
                    name = line.split("::", 1)[1].split()[0]
                    failed.add(name)
        for c, name in items:
            if name in passed:
                c.evidence_found = True
                c.evidence_where = f"pytest passed ({source})"
            elif name in failed:
                c.evidence_found = False
                c.evidence_where = f"pytest failed ({source})"
            else:
                c.evidence_found = False
                c.evidence_where = f"pytest did not collect ({source})"

def _attest_declared(root, c):
    p = root / c.source
    c.evidence_found = p.exists()
    c.evidence_where = "file exists" if c.evidence_found else "file missing"


def _attest_standards_conformant(root, c):
    p = root / c.source
    try:
        d = json.loads(p.read_text())
        c.evidence_found = bool(d.get("conformant"))
        c.evidence_where = f"artifact field: conformant={d.get('conformant')}"
    except Exception:
        c.evidence_found = False
        c.evidence_where = "artifact unreadable"


def _attest_standards_generated(root, c):
    """Re-run the attest generator and confirm nothing is omitted."""
    code, out, err = _run(
        ["python", "packages/attest/standards.py"], root, timeout=60,
    )
    if code == 0 and "omitted" not in out:
        c.evidence_found = True
        c.evidence_where = "regenerated with 0 omitted"
    else:
        c.evidence_found = False
        c.evidence_where = f"regeneration had omissions or rc={code}"


def _attest_standards_all_verified(root, c):
    """Re-run standards.py, read the fresh artifact, confirm verified==count."""
    code, out, err = _run(
        ["python", "packages/attest/standards.py"], root, timeout=60,
    )
    if code != 0:
        c.evidence_found = False
        c.evidence_where = f"regeneration rc={code}"
        return
    artifact = root / c.source
    try:
        d = json.loads(artifact.read_text())
        ok = d.get("count") == d.get("verified")
        c.evidence_found = bool(ok)
        c.evidence_where = f"count={d.get('count')} verified={d.get('verified')}"
    except Exception as e:
        c.evidence_found = False
        c.evidence_where = f"reread failed: {e}"


def _attest_bridge_regimes(root, c):
    """Re-classify the corpus and compare to the bridge report."""
    try:
        sys.path.insert(0, str(root / "packages" / "buildability" / "src"))
        from buildability import spec_from_file, evaluate
        from collections import Counter
        name = c.id.split(":", 2)[1]  # e.g. mesh/specs_uci
        d = root / name
        if not d.exists():
            c.evidence_found = False
            c.evidence_where = f"corpus {name} missing"
            return
        specs = [spec_from_file(p) for p in sorted(d.glob("*.json"))]
        dist = dict(Counter(evaluate(s).regime for s in specs))
        # Extract the claimed distribution from the text.
        br = json.loads((root / "bridge" / "report.json").read_text())
        claimed = None
        for sec in br.get("sections", []):
            if sec.get("name") == name:
                claimed = sec.get("regimes")
                break
        c.evidence_found = (dist == claimed)
        c.evidence_where = f"regenerated={dist} claimed={claimed}"
    except Exception as e:
        c.evidence_found = False
        c.evidence_where = f"reeval failed: {e}"


def _attest_mesh_counts(root, c):
    """Re-run mesh factory, compare counts."""
    code, out, err = _run(
        ["python", "mesh/mesh.py"], root, timeout=120,
    )
    if code != 0:
        c.evidence_found = False
        c.evidence_where = f"mesh re-run rc={code}"
        return
    try:
        report_path = root / "mesh" / "report.json"
        fresh = json.loads(report_path.read_text())
        stored_claim_text = c.text
        # Compare to the current on-disk report.
        fresh_emitted = fresh.get("emitted")
        fresh_refused = fresh.get("skipped_invalid")
        c.evidence_found = f"emitted={fresh_emitted}" in stored_claim_text and \
                           f"refused={fresh_refused}" in stored_claim_text
        c.evidence_where = f"fresh emitted={fresh_emitted} refused={fresh_refused}"
    except Exception as e:
        c.evidence_found = False
        c.evidence_where = f"reread failed: {e}"


def _attest_central_ran(root, c):
    """Re-run the central build script."""
    spec_name = c.text.split(" ", 1)[0]
    script = root / "experiments" / "central" / "build_uci_cms.py"
    if not script.exists():
        c.evidence_found = False
        c.evidence_where = "build script missing"
        return
    code, out, err = _run(["python", str(script)], root, timeout=60)
    if code != 0:
        c.evidence_found = False
        c.evidence_where = f"re-run rc={code}"
        return
    try:
        d = json.loads((root / "experiments" / "central" / "outcome.json").read_text())
        c.evidence_found = d.get("run_succeeded") is True
        c.evidence_where = f"fresh run_succeeded={d.get('run_succeeded')}"
    except Exception as e:
        c.evidence_found = False
        c.evidence_where = f"reread failed: {e}"


def _attest_refused(root, c):
    try:
        sys.path.insert(0, str(root / "packages" / "buildability" / "src"))
        from buildability import spec_from_file, evaluate
        spec = root / "mesh" / "specs_counterexample" / "COUNTEREXAMPLE-DUPLICATE-OWNER.json"
        v = evaluate(spec_from_file(spec))
        c.evidence_found = v.regime == "INCOHERENT"
        c.evidence_where = f"fresh regime={v.regime}"
    except Exception as e:
        c.evidence_found = False
        c.evidence_where = f"reeval failed: {e}"


ROUTES = {
    "tested": _attest_test,
    "declared": _attest_declared,
    "conformant": _attest_standards_conformant,
    "refused": _attest_refused,
}


def attest_all(root: Path, claims: list[Claim]) -> list[Claim]:
    """Attest every claim.

    Test claims are collected and batched — pytest runs once per source
    file, not once per test. Everything else routes as before.
    """
    tested: list[Claim] = []
    for c in claims:
        if c.kind == "tested":
            tested.append(c)
            continue
        fn = ROUTES.get(c.kind)
        if fn is not None:
            fn(root, c)
            continue
        if c.id.startswith("standards:") and c.id.endswith(":all-verified"):
            _attest_standards_all_verified(root, c)
        elif c.id.startswith("standards:") and c.id.endswith(":generated"):
            _attest_standards_generated(root, c)
        elif c.id.startswith("standards:INDEX"):
            _attest_standards_generated(root, c)
        elif c.id.startswith("bridge:"):
            _attest_bridge_regimes(root, c)
        elif c.id.startswith("mesh:"):
            _attest_mesh_counts(root, c)
        elif c.id.startswith("central:") and c.id.endswith(":ran"):
            _attest_central_ran(root, c)
        else:
            c.evidence_found = False
            c.evidence_where = "no attester wired"
    if tested:
        _attest_tests_batch(root, tested)
    return claims
