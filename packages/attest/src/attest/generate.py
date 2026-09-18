"""Generate standards artifacts from evidence. Refuse when evidence is absent."""
from __future__ import annotations
import json
from pathlib import Path
from .evidence import Evidence


ARTIFACTS = [
    "requirements_specification",
    "traceability_matrix",
    "test_documentation",
    "provenance_record",
    "configuration_management",
    "gate_conformance",
]


def requirements_specification(ev: Evidence) -> dict:
    """One requirement per gate. Each has a criterion and a verification method.
    The method names the test that verifies it, or says 'unverified' if none."""
    gates = {}
    for m in ev.modules:
        for g in m.get("gates", []):
            gates[g] = m["file"]
    if not gates:
        return {"status": "omitted", "reason": "no Gate enum found in packages/"}

    tests_by_gate = _match_tests_to_gates(ev.tests, gates)

    reqs = []
    for i, (gate, file) in enumerate(sorted(gates.items()), 1):
        reqs.append({
            "id": f"REQ-{gate}",
            "gate": gate,
            "defined_in": file,
            "criterion": f"evaluate() returns a verdict determined by {gate}",
            "verification": tests_by_gate.get(gate, []),
            "verified": bool(tests_by_gate.get(gate)),
        })
    return {
        "status": "generated",
        "count": len(reqs),
        "verified": sum(1 for r in reqs if r["verified"]),
        "requirements": reqs,
    }


def traceability_matrix(ev: Evidence) -> dict:
    """Every test mapped to the requirement it verifies. If a test names no
    requirement, it is recorded as untraced rather than omitted."""
    gates = set()
    for m in ev.modules:
        gates.update(m.get("gates", []))
    matched = _match_tests_to_gates(ev.tests, gates)
    test_to_gate = {}
    for g, names in matched.items():
        for n in names:
            test_to_gate[n] = g
    rows = []
    for t in ev.tests:
        target = None
        g = test_to_gate.get(t["name"])
        if g is not None:
            target = f"REQ-{g}"
        rows.append({
            "test": t["name"],
            "file": t["file"],
            "line": t["line"],
            "requirement": target,
            "traced": target is not None,
        })
    return {
        "status": "generated",
        "count": len(rows),
        "traced": sum(1 for r in rows if r["traced"]),
        "untraced": sum(1 for r in rows if not r["traced"]),
        "rows": rows,
    }


def test_documentation(ev: Evidence) -> dict:
    """IEEE 829-shaped test case records, derived from AST."""
    if not ev.tests:
        return {"status": "omitted", "reason": "no test functions found"}
    cases = []
    for t in ev.tests:
        cases.append({
            "test_id": f"{t['file']}::{t['name']}",
            "location": {"file": t["file"], "line": t["line"]},
            "purpose": t["doc"] or "(no docstring)",
            "type": "unit",
        })
    return {
        "status": "generated",
        "count": len(cases),
        "cases": cases,
    }


def provenance_record(ev: Evidence) -> dict:
    """W3C PROV-shaped record of the repo's current state."""
    if not ev.commits:
        return {"status": "omitted", "reason": "no git history available"}
    head = ev.commits[0]
    entities = [{"id": "repo", "type": "prov:Collection"}]
    activities = []
    agents = {}
    for c in ev.commits:
        activities.append({
            "id": f"commit:{c['hash'][:12]}",
            "type": "prov:Activity",
            "startedAtTime": c["date"],
            "used": "repo",
            "generated": f"commit:{c['hash'][:12]}",
            "label": c["subject"],
        })
        agents[c["author"]] = {"id": c["author"], "type": "prov:Person"}
    return {
        "status": "generated",
        "head": head["hash"],
        "commit_count": len(ev.commits),
        "dirty": ev.git_dirty,
        "entities": entities,
        "activities": activities,
        "agents": list(agents.values()),
    }


def configuration_management(ev: Evidence) -> dict:
    """CM baseline: what is tracked, what is not, and where the boundary is."""
    root = ev.root
    gitignore = root / ".gitignore"
    ignored_patterns = []
    if gitignore.exists():
        for line in gitignore.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                ignored_patterns.append(line)
    generated = []
    for d in ["mesh/emitted", "mesh/specs", "mesh/report.json",
              "bridge/report.json"]:
        if (root / d).exists():
            generated.append(d)
    tracked_ignored = []
    for d in generated:
        r = _git_tracked(root, d)
        if r:
            tracked_ignored.append(d)
    return {
        "status": "generated",
        "vcs": "git",
        "dirty": ev.git_dirty,
        "ignored_patterns": ignored_patterns,
        "generated_paths": generated,
        "conflict": tracked_ignored,
        "conflict_free": not tracked_ignored,
    }


def _git_tracked(root, path):
    import subprocess
    try:
        r = subprocess.run(["git", "ls-files", path], cwd=root,
                           capture_output=True, text=True, timeout=5)
        return bool(r.stdout.strip())
    except Exception:
        return False


def _match_tests_to_gates(tests, gates):
    """Map each gate name to the tests that reference it.

    Matching is on whole tokens: gate names are converted to the form
    that appears in test identifiers (lowercase, underscores preserved).
    The match is anchored on word boundaries so 'g1' does not match
    'g1_5', 'g3_g4_g5', or 'g1_and_g2' ambiguously — the longest gate
    name that the test name contains wins.
    """
    import re
    by_gate = {g: [] for g in gates}
    sorted_gates = sorted(gates, key=len, reverse=True)
    for t in tests:
        name = t["name"].lower()
        for g in sorted_gates:
            needle = g.lower()
            pattern = r"(^|_)" + re.escape(needle) + r"(_|$)"
            if re.search(pattern, name):
                by_gate[g].append(t["name"])
                break
    return by_gate


def gate_conformance(ev: Evidence) -> dict:
    """For each gate, the tests that reference it, whether they pass is
    recorded externally. This artifact records the conformance surface."""
    gates = {}
    for m in ev.modules:
        for g in m.get("gates", []):
            gates[g] = {"defined_in": m["file"], "tests": []}
    matched = _match_tests_to_gates(ev.tests, gates.keys())
    for g, names in matched.items():
        gates[g]["tests"] = names
    missing = [g for g, info in gates.items() if not info["tests"]]
    return {
        "status": "generated",
        "gates": gates,
        "missing_test_coverage": missing,
        "conformant": not missing,
    }


GENERATORS = {
    "requirements_specification": requirements_specification,
    "traceability_matrix": traceability_matrix,
    "test_documentation": test_documentation,
    "provenance_record": provenance_record,
    "configuration_management": configuration_management,
    "gate_conformance": gate_conformance,
}


def generate_all(ev: Evidence) -> dict:
    out = {}
    for name, fn in GENERATORS.items():
        try:
            out[name] = fn(ev)
        except Exception as e:
            out[name] = {"status": "error", "reason": f"{type(e).__name__}: {e}"}
    return out
