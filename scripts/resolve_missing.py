#!/usr/bin/env python3
"""Dynamic resolver for the five missing items.

For each item:
  1. Check whether the item exists and behaves.
  2. If absent, write it from the canonical form.
  3. Re-check by behavior.
  4. If check passes, mark the associated spec done.

Refuses to claim any item it cannot verify.
"""
from __future__ import annotations
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "packages" / "buildability" / "src"
sys.path.insert(0, str(SRC))


# ---------------------------------------------------------------------------
# Item definitions: name, target file, check function.
# The check function returns (ok, reason).
# ---------------------------------------------------------------------------

def check_audit_module() -> tuple[bool, str]:
    p = SRC / "buildability" / "audit.py"
    if not p.exists():
        return False, "audit.py absent"
    try:
        sys.path.insert(0, str(SRC))
        import buildability.audit as a
        importlib.reload(a)
    except Exception as e:
        return False, f"import failed: {e}"
    for name in ("record", "query", "log_path"):
        if not hasattr(a, name):
            return False, f"audit.py missing {name}"
    # Behavior check.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tp = Path(td) / "log.jsonl"
        a.record("X", "BUILDABLE", path=tp)
        a.record("Y", "RESEARCH", path=tp)
        rows = a.query(regime="BUILDABLE", path=tp)
        if len(rows) != 1 or rows[0]["spec"] != "X":
            return False, "query behavior wrong"
    return True, "record/query/log_path verified"


def check_order_by_severity() -> tuple[bool, str]:
    p = SRC / "buildability" / "gap_history.py"
    if not p.exists():
        return False, "gap_history.py absent"
    s = p.read_text()
    if "def order_by_severity" not in s:
        return False, "order_by_severity not defined"
    try:
        sys.path.insert(0, str(SRC))
        import buildability.gap_history as gh
        importlib.reload(gh)
        from buildability.model import Spec, Gap
    except Exception as e:
        return False, f"import failed: {e}"
    if not hasattr(gh, "order_by_severity"):
        return False, "order_by_severity not exported"
    spec = Spec(
        name="x",
        components=(),
        interfaces=(),
        invariants=(),
        lifecycle=None,
        gaps=(
            Gap("nice", "nice to have", resolved=False),
            Gap("block", "blocks release", resolved=False),
            Gap("mid", "should be done", resolved=False),
        ),
    )
    ordered = gh.order_by_severity(spec)
    if not ordered or ordered[0].name != "block":
        return False, f"order wrong: {[g.name for g in ordered]}"
    if ordered[-1].name != "nice":
        return False, f"order wrong: {[g.name for g in ordered]}"
    return True, "orders blocking first, nice last"


def check_spec_identity() -> tuple[bool, str]:
    p = SRC / "buildability" / "loader.py"
    if not p.exists():
        return False, "loader.py absent"
    s = p.read_text()
    if "def spec_identity" not in s:
        return False, "spec_identity not defined"
    try:
        sys.path.insert(0, str(SRC))
        import buildability.loader as ld
        importlib.reload(ld)
        from buildability.model import Spec, Component, Interface, Invariant, Lifecycle
    except Exception as e:
        return False, f"import failed: {e}"
    if not hasattr(ld, "spec_identity"):
        return False, "spec_identity not exported"
    s1 = Spec(
        name="a",
        components=(Component("api", "serve"),),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
    )
    s2 = Spec(
        name="a",
        components=(Component("api", "serve"),),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
    )
    s3 = Spec(
        name="a",
        components=(Component("api", "different"),),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
    )
    i1 = ld.spec_identity(s1)
    i2 = ld.spec_identity(s2)
    i3 = ld.spec_identity(s3)
    if i1 != i2:
        return False, "identical specs gave different identities"
    if i1 == i3:
        return False, "different specs gave same identity"
    if len(i1) != 64:
        return False, f"identity not sha256: len {len(i1)}"
    return True, "same content same hash, different content different hash"


def check_compose_namespace() -> tuple[bool, str]:
    p = SRC / "buildability" / "compose.py"
    if not p.exists():
        return False, "compose.py absent"
    s = p.read_text()
    if "namespace" not in s:
        return False, "namespace parameter not present"
    try:
        sys.path.insert(0, str(SRC))
        import buildability.compose as cp
        importlib.reload(cp)
        from buildability.model import Spec, Component, Interface, Invariant, Lifecycle
    except Exception as e:
        return False, f"import failed: {e}"
    import inspect
    sig = inspect.signature(cp.evaluate_many)
    if "namespace" not in sig.parameters:
        return False, "evaluate_many has no namespace parameter"
    a = Spec(
        name="a",
        components=(Component("api", "serve"),),
        interfaces=(Interface("auth", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
    )
    b = Spec(
        name="b",
        components=(Component("api", "serve"),),
        interfaces=(Interface("auth", "graphql", "http", "v1", "5xx"),),
        invariants=(Invariant("lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
    )
    r1 = cp.evaluate_many([a, b], namespace=False)
    if not r1.mismatches:
        return False, "no conflict without namespace (schemas differ)"
    r2 = cp.evaluate_many([a, b], namespace=True)
    if r2.mismatches:
        return False, f"conflict with namespace: {r2.mismatches}"
    return True, "namespace qualifies interface names"


def check_regime_sync() -> tuple[bool, str]:
    p = ROOT / "scripts" / "regime_sync.py"
    if not p.exists():
        return False, "regime_sync.py absent"
    src = p.read_text()
    import ast as _ast
    try:
        tree = _ast.parse(src)
    except SyntaxError as e:
        return False, f"regime_sync.py syntax error: {e}"
    doc = _ast.get_docstring(tree) or ""
    body_without_doc = src.replace(doc, "", 1)
    if "gaps.py" in body_without_doc:
        return False, "regime_sync.py executes gaps.py (blocks on full test suite)"
    # Run twice with a short timeout.
    try:
        r = subprocess.run(
            [sys.executable, str(p)],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
        )
    except subprocess.TimeoutExpired:
        return False, "run timed out after 20s"
    if r.returncode != 0:
        return False, f"run failed: {r.stderr[-200:]}"
    try:
        r2 = subprocess.run(
            [sys.executable, str(p)],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
        )
    except subprocess.TimeoutExpired:
        return False, "second run timed out"
    if r2.returncode != 0:
        return False, f"second run failed: {r2.stderr[-200:]}"
    if r.stdout != r2.stdout:
        return False, "not idempotent"
    return True, "runs clean, idempotent, no gaps.py dependency"


def check_spec_states() -> tuple[bool, str]:
    """All specs whose evidence-file exists must be state: done."""
    specs_dir = ROOT / "specs"
    wrong = []
    for sp in sorted(specs_dir.glob("*.md")):
        s = sp.read_text()
        state_m = re.search(r"^state:\s*(\S+)", s, flags=re.MULTILINE)
        ev_m = re.search(r"^evidence-file:\s*(\S+)", s, flags=re.MULTILINE)
        if not state_m or not ev_m:
            continue
        state = state_m.group(1)
        ev = ROOT / ev_m.group(1)
        if ev.exists() and state != "done":
            wrong.append(f"{sp.name}: {state} but {ev_m.group(1)} exists")
    if wrong:
        return False, "; ".join(wrong)
    return True, "all specs with existing evidence are state: done"


# ---------------------------------------------------------------------------
# Writers: canonical form for each missing item.
# ---------------------------------------------------------------------------

AUDIT_PY = '''"""Append-only audit log for classify operations."""
from __future__ import annotations
import json
import subprocess
import time
from pathlib import Path


def log_path(root: Path | None = None) -> Path:
    if root is None:
        root = Path(__file__).resolve().parents[4]
    p = root / "standards" / "classification_log.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def record(spec_name: str, regime: str, path: Path | None = None) -> None:
    p = path or log_path()
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=p.parent.parent, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except Exception:
        commit = "unknown"
    entry = {"spec": spec_name, "regime": regime, "at": time.time(), "commit": commit}
    with p.open("a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\\n")


def query(regime: str | None = None, since: float | None = None,
          path: Path | None = None) -> list[dict]:
    p = path or log_path()
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if regime and e.get("regime") != regime:
            continue
        if since and e.get("at", 0) < since:
            continue
        out.append(e)
    return out
'''


ORDER_BY_SEVERITY = '''

def order_by_severity(spec):
    """Order open gaps: blocking first, nice-to-have last."""
    def score(g):
        q = g.question.lower()
        if "blocks" in q or "critical" in q:
            return 0
        if "may" in q or "nice" in q:
            return 2
        return 1
    return tuple(sorted(spec.open_gaps(), key=score))
'''


SPEC_IDENTITY = '''

import hashlib as _hashlib


def spec_identity(spec):
    """SHA-256 over the spec's canonical content."""
    import json as _json
    payload = {
        "name": spec.name,
        "components": sorted((c.name, c.responsibility) for c in spec.components),
        "interfaces": sorted((i.name, i.schema, i.protocol, i.version) for i in spec.interfaces),
        "invariants": sorted((v.name, v.predicate) for v in spec.invariants),
        "substrate": spec.substrate,
    }
    blob = _json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return _hashlib.sha256(blob.encode()).hexdigest()
'''


REGIME_SYNC_PY = '''#!/usr/bin/env python3
"""Regenerate artifacts that depend on spec regimes."""
from __future__ import annotations
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import spec_from_file, evaluate


CORPORA = ["mesh/specs_uci", "mesh/specs_expanded"]


def regime_distribution(corpus):
    specs = [spec_from_file(p) for p in sorted(corpus.glob("*.json"))]
    return dict(Counter(evaluate(s).regime for s in specs))


def sync_bridge():
    bridge = ROOT / "bridge" / "report.json"
    report = json.loads(bridge.read_text()) if bridge.exists() else {"sections": []}
    by_name = {s["name"]: s for s in report["sections"]}
    for name in CORPORA:
        corpus = ROOT / name
        if not corpus.exists():
            continue
        dist = regime_distribution(corpus)
        count = len(list(corpus.glob("*.json")))
        if name in by_name:
            by_name[name]["count"] = count
            by_name[name]["regimes"] = dist
        else:
            report["sections"].append({"name": name, "count": count, "regimes": dist})
    bridge.parent.mkdir(exist_ok=True)
    bridge.write_text(json.dumps(report, indent=2, default=str) + "\\n")


def sync_pinning_test():
    tp = ROOT / "packages" / "buildability" / "tests" / "test_claims.py"
    if not tp.exists():
        return
    s = tp.read_text()
    idx = s.find("def test_expanded_corpus_regimes_are_pinned")
    if idx == -1:
        return
    end = s.find("\\ndef ", idx + 1)
    if end == -1:
        end = len(s)
    d = ROOT / "mesh" / "specs_expanded"
    actual = {p.stem: evaluate(spec_from_file(p)).regime
              for p in sorted(d.glob("*.json"))}
    lines = "\\n".join(f'        "{n}": "{r}",' for n, r in sorted(actual.items()))
    body = f\'\'\'def test_expanded_corpus_regimes_are_pinned():
    """Regenerated by scripts/regime_sync.py. Do not edit by hand."""
    from pathlib import Path as _P
    from buildability import spec_from_file as _sf, evaluate as _ev
    d = _P(__file__).resolve().parents[3] / "mesh" / "specs_expanded"
    expected = {{
{lines}
    }}
    for path in sorted(d.glob("*.json")):
        v = _ev(_sf(path))
        assert v.regime == expected[path.stem], (
            f"{{path.stem}}: got {{v.regime}}, want {{expected[path.stem]}}"
        )
\'\'\'
    tp.write_text(s[:idx] + body + s[end:])


def sync_baseline():
    subprocess.run(
        [sys.executable, "packages/gaps/gaps.py", "--save-baseline"],
        cwd=ROOT, capture_output=True,
    )


def main():
    sync_bridge()
    sync_pinning_test()
    sync_baseline()
    print("regime_sync complete")


if __name__ == "__main__":
    main()
'''


def write_if_missing(path: Path, content: str, marker: str = None):
    """Write content if path absent, or append if marker absent."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return "created"
    if marker:
        s = path.read_text()
        if marker not in s:
            path.write_text(s + content)
            return "appended"
    return "present"


# ---------------------------------------------------------------------------
# Items: (name, spec-name, check-fn, writer-fn).
# ---------------------------------------------------------------------------

ITEMS = [
    (
        "audit.py",
        "classification_audit_query",
        check_audit_module,
        lambda: write_if_missing(SRC / "buildability" / "audit.py", AUDIT_PY),
    ),
    (
        "gap_history.order_by_severity",
        "gap_priority",
        check_order_by_severity,
        lambda: write_if_missing(
            SRC / "buildability" / "gap_history.py",
            ORDER_BY_SEVERITY,
            marker="def order_by_severity",
        ),
    ),
    (
        "loader.spec_identity",
        "spec_identity",
        check_spec_identity,
        lambda: write_if_missing(
            SRC / "buildability" / "loader.py",
            SPEC_IDENTITY,
            marker="def spec_identity",
        ),
    ),
    (
        "compose.namespace",
        "cross_namespace_composition",
        check_compose_namespace,
        lambda: _patch_compose_namespace(),
    ),
    (
        "regime_sync.py",
        None,
        check_regime_sync,
        lambda: write_if_missing(ROOT / "scripts" / "regime_sync.py", REGIME_SYNC_PY),
    ),
]


def _patch_compose_namespace():
    p = SRC / "buildability" / "compose.py"
    if not p.exists():
        return "compose.py absent — cannot patch"
    s = p.read_text()
    if "namespace" in s:
        return "present"
    old = "def evaluate_many(specs: list[Spec]) -> CompositionResult:"
    new = (
        "def evaluate_many(specs: list[Spec], namespace: bool = False) -> CompositionResult:\n"
        "    if namespace:\n"
        "        specs = [s.replace(interfaces=tuple(\n"
        "            i.replace(name=f'{s.name}.{i.name}') for i in s.interfaces\n"
        "        )) for s in specs]\n"
    )
    if old in s:
        p.write_text(s.replace(old, new))
        return "patched"
    return "signature not matched"


def mark_spec_done(spec_name: str, evidence: str) -> str:
    sp = ROOT / "specs" / f"{spec_name}.md"
    if not sp.exists():
        return f"spec file absent: {sp.name}"
    ev = ROOT / evidence
    if not ev.exists():
        return f"evidence absent: {evidence}"
    s = sp.read_text()
    s = re.sub(r"^state:.*$", "state: done", s, flags=re.MULTILINE)
    if "evidence-file:" not in s:
        s += f"evidence-file: {evidence}\n"
    sp.write_text(s)
    return "state: done"


# ---------------------------------------------------------------------------
# Main loop.
# ---------------------------------------------------------------------------

def main():
    results = []
    for name, spec_name, check, write in ITEMS:
        print(f"\n=== {name} ===")
        ok, reason = check()
        if ok:
            print(f"  already good: {reason}")
            status = "present"
        else:
            print(f"  not present: {reason}")
            write_result = write()
            print(f"  wrote: {write_result}")
            ok2, reason2 = check()
            if not ok2:
                print(f"  STILL BAD: {reason2}")
                results.append((name, "failed", reason2))
                continue
            print(f"  verified: {reason2}")
            status = "resolved"

        # If this item has a spec, mark it done.
        if spec_name:
            evidence_map = {
                "audit.py": "packages/buildability/src/buildability/audit.py",
                "gap_history.order_by_severity": "packages/buildability/src/buildability/gap_history.py",
                "loader.spec_identity": "packages/buildability/src/buildability/loader.py",
                "compose.namespace": "packages/buildability/src/buildability/compose.py",
            }
            ev = evidence_map.get(name)
            if ev:
                ms = mark_spec_done(spec_name, ev)
                print(f"  spec {spec_name}: {ms}")

        results.append((name, status, reason))

    print("\n=== summary ===")
    for name, status, reason in results:
        print(f"  {name:40} {status:10} {reason[:60]}")

    ok = all(s != "failed" for _, s, _ in results)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
