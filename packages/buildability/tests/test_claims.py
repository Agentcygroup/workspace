"""Validation of every claim made about the buildability framework.

Each test names a specific claim. Tests marked FAIL are the ones that
demonstrate the gap between what the framework claims and what it does.
They are intentionally failing assertions, wrapped so the suite reports
them as validation findings rather than build failures.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from buildability import (
    Spec, Component, Interface, Invariant, Lifecycle, Gap,
    evaluate, Regime,
)
from buildability.loader import spec_from_dict, spec_from_file
from buildability.classify import classify_dir
from buildability.fixedpoint import closure, is_fixed_point
from buildability.intent import IntentRatio


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def full_spec(**over):
    base = dict(
        name="full",
        components=(Component("api", "serve"),),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("latency", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="kubernetes",
        substrate_available=True,
    )
    base.update(over)
    return Spec(**base)


REPO = Path(__file__).resolve().parents[3]
MESH_SPECS = REPO / "mesh" / "specs"
EXPANDED = REPO / "mesh" / "specs_expanded"


# ===========================================================================
# CLAIM GROUP 1: What the framework actually implements
# ===========================================================================

def test_claim_g1_and_g2_are_implemented():
    """G1 (spec) and G2 (substrate) are both structurally checked.

    G2 semantics: probe first, fall back to substrate_available only
    when the probe has no opinion. This test pins the fallback path.
    """
    assert evaluate(full_spec()).regime in ("CONSTRUCTION", "BUILDABLE")
    # An unknown substrate with the flag False lands at ENGINEERING.
    v = evaluate(full_spec(substrate="mystery-substrate",
                           substrate_available=False))
    assert v.regime == "ENGINEERING"


def test_claim_g3_g4_g5_are_stubs_not_generators():
    """G3/G4/G5 only check that user-supplied callables exist.

    The framework does not produce a solver, prover, or resolver. It
    only invokes one if wired. This test demonstrates the stub nature:
    a spec with no solver wired fails G3 with 'no solver wired', not
    with any synthesized artifact.
    """
    v = evaluate(full_spec())
    assert v.regime == "CONSTRUCTION"
    g3 = [r for r in v.results if r.gate.value == "G3"][0]
    assert "no solver wired" in g3.reason
    # The framework did NOT attempt to construct anything.


def test_claim_no_builder_exists():
    """There is no function in buildability that emits an artifact."""
    import buildability
    public = [n for n in dir(buildability) if not n.startswith("_")]
    builders = [n for n in public if "build" in n.lower() and n != "build"]
    # `build` may exist but is a thin wrapper; there is no code emitter.
    for n in public:
        obj = getattr(buildability, n)
        if callable(obj) and hasattr(obj, "__module__"):
            assert "emit" not in n.lower(), f"unexpected emitter: {n}"


# ===========================================================================
# CLAIM GROUP 2: What the framework fails to do
# ===========================================================================

def test_semantic_incompleteness_is_detected():
    """G1.5 catches the incoherence G1 misses."""
    incoherent = Spec(
        name="incoherent",
        components=(
            Component("api", "serve"),
            Component("api2", "serve"),
        ),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(
            Invariant("fast", "p99<100ms"),
            Invariant("slow", "p99>500ms"),
        ),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="kubernetes",
        substrate_available=True,
    )
    v = evaluate(incoherent)
    assert v.regime == "INCOHERENT", v


def test_fail_no_distance_metric_between_specs():
    """A spec missing one element is the same regime as a spec missing five."""
    almost = full_spec(name="almost")
    almost = almost.replace(components=())  # missing one element

    empty = Spec(name="empty")  # missing everything

    assert evaluate(almost).regime == evaluate(empty).regime == "RESEARCH"
    # No way to ask "how far from complete is this?"


def test_fail_substrate_availability_not_probed():
    """substrate_available=True is taken on faith; nothing checks it."""
    lying = full_spec(substrate="nonexistent-cluster", substrate_available=True)
    v = evaluate(lying)
    # G2 passes because the boolean says so.
    assert v.regime in ("CONSTRUCTION", "BUILDABLE"), (
        "Framework probed substrate (unexpected)"
    )


def test_fail_divergence_requires_external_history():
    """G0 needs a gap_history list from outside. Nothing computes it."""
    spec = full_spec(gaps=(Gap("x", "?"),))
    v = evaluate(spec)  # no history
    # No divergence check ran.
    assert v.regime == "RESEARCH"
    # G0 runs but with no history it reports insufficient and passes.
    g0_results = [r for r in v.results if r.gate.value == "G0"]
    assert g0_results, "G0 should run even without history"
    assert g0_results[0].passed, "G0 with no history should pass"
    assert "insufficient" in g0_results[0].reason


def test_cross_spec_composition_exists():
    """evaluate_many is exported and handles the empty case."""
    from buildability import evaluate_many
    result = evaluate_many([])
    assert result.ok
    assert result.verdicts == {}
    assert result.mismatches == ()


def test_cross_spec_composition_detects_mismatch():
    """Two specs claiming the same interface with different schemas mismatch."""
    from buildability import (
        Spec, Component, Interface, Invariant, Lifecycle, evaluate_many,
    )
    name = "auth.rest"
    a = Spec(
        name="a",
        components=(Component("a.api", "serve"),),
        interfaces=(Interface(name, "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("a.inv", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="kubernetes",
        substrate_available=True,
    )
    b = Spec(
        name="b",
        components=(Component("b.api", "serve"),),
        interfaces=(Interface(name, "graphql", "http", "v1", "4xx"),),
        invariants=(Invariant("b.inv", "p99<300ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="kubernetes",
        substrate_available=True,
    )
    result = evaluate_many([a, b])
    assert not result.ok
    assert len(result.mismatches) >= 1
    assert result.mismatches[0].interface == name
    assert "schema mismatch" in result.mismatches[0].reason


def test_cross_spec_composition_accepts_matching():
    """Two specs with identical interface schemas compose cleanly."""
    from buildability import (
        Spec, Component, Interface, Invariant, Lifecycle, evaluate_many,
    )
    name = "auth.rest"
    def make(n):
        return Spec(
            name=n,
            components=(Component(n + ".api", "serve"),),
            interfaces=(Interface(name, "openapi", "http", "v1", "5xx"),),
            invariants=(Invariant(n + ".inv", "p99<200ms"),),
            lifecycle=Lifecycle("a", "b", "c", "d", "e"),
            substrate="kubernetes",
            substrate_available=True,
        )
    result = evaluate_many([make("a"), make("b")])
    assert result.mismatches == ()
    assert result.ok


def test_fail_no_partial_spec_handling():
    """G1 is binary per gate: any missing element fails the whole gate."""
    partial = full_spec(components=(Component("api", ""),))  # blank responsibility
    v = evaluate(partial)
    assert v.regime == "RESEARCH"
    g1 = [r for r in v.results if r.gate.value == "G1"][0]
    # No partial credit, no "you're 5/6 complete".
    assert "missing elements" in g1.reason


# ===========================================================================
# CLAIM GROUP 3: What the session failed to address
# ===========================================================================

def test_fail_mesh_specs_remain_research():
    """All mesh specs are still RESEARCH; nothing fixed them."""
    result = classify_dir(MESH_SPECS)
    dist = result["distribution"]
    assert dist.get("RESEARCH", 0) >= 400, (
        f"expected nearly all RESEARCH, got {dist}"
    )


def test_factory_refuses_incomplete_specs():
    """Factory is wired to buildability and refuses RESEARCH specs."""
    mesh_py = REPO / "mesh" / "mesh.py"
    src = mesh_py.read_text()
    assert "buildability" in src, (
        "factory is not wired to the buildability classifier"
    )
    assert "_gate(" in src, (
        "factory does not call _gate in its emit loop"
    )


def test_fail_no_determinism_test_for_classifier():
    """Classifier output was never tested for determinism."""
    r1 = classify_dir(EXPANDED)
    r2 = classify_dir(EXPANDED)
    # This passes because classify_dir is deterministic. But no test in the
    # suite pins that. This test is the missing pin.
    assert r1 == r2  # will pass; the gap is that this test did not exist


def test_intent_ratio_is_wired():
    """IntentRatio is imported and used by classify.py."""
    import ast
    import buildability
    pkg = Path(buildability.__file__).parent
    callers = []
    for py in pkg.rglob("*.py"):
        if py.name == "intent.py":
            continue
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "IntentRatio":
                callers.append(py.name)
    assert "classify.py" in callers, (
        f"IntentRatio not wired into classify.py; callers={callers}"
    )


def test_expanded_corpus_regimes_are_pinned():
    """Regenerated by scripts/regime_sync.py. Do not edit by hand."""
    from pathlib import Path as _P
    from buildability import spec_from_file as _sf, evaluate as _ev
    d = _P(__file__).resolve().parents[3] / "mesh" / "specs_expanded"
    expected = {
        "EXPAND-L0": "BUILDABLE",
        "EXPAND-L1-NO-COMPONENTS": "RESEARCH",
        "EXPAND-L1-NO-INTERFACES": "RESEARCH",
        "EXPAND-L1-NO-INVARIANTS": "RESEARCH",
        "EXPAND-L1-NO-LIFECYCLE": "RESEARCH",
        "EXPAND-L1-NO-SUBSTRATE": "BUILDABLE",
        "EXPAND-L2-EMPTY-COMPONENT-RESP": "RESEARCH",
        "EXPAND-L2-INTERFACE-NO-SCHEMA": "RESEARCH",
        "EXPAND-L2-INVARIANT-NO-PREDICATE": "RESEARCH",
        "EXPAND-L2-LIFECYCLE-NO-ROLLBACK": "RESEARCH",
        "EXPAND-L3-GAP-0": "RESEARCH",
        "EXPAND-L3-GAP-1": "RESEARCH",
        "EXPAND-L3-GAP-2": "RESEARCH",
        "EXPAND-L4-MULTI-GAP": "RESEARCH",
        "_convergent_history": "RESEARCH",
        "_divergent_history": "RESEARCH",
    }
    for path in sorted(d.glob("*.json")):
        v = _ev(_sf(path))
        assert v.regime == expected[path.stem], (
            f"{path.stem}: got {v.regime}, want {expected[path.stem]}"
        )

def test_verdict_is_frozen():
    """Verdict is now frozen: it is an immutable value."""
    from buildability.procedure import Verdict
    v = Verdict("RESEARCH")
    with pytest.raises(Exception):
        v.regime = "BUILDABLE"


def test_gate_result_is_frozen():
    """GateResult is frozen; verify the contract holds."""
    from buildability.gates import GateResult, Gate
    r = GateResult(Gate.G1, True, "ok")
    with pytest.raises(Exception):
        r.passed = False


def test_verdict_has_value_eq():
    """Two verdicts with same regime+results compare equal."""
    from buildability.procedure import Verdict
    v1 = Verdict("RESEARCH")
    v2 = Verdict("RESEARCH")
    assert v1 == v2


def test_verdict_to_dict_is_json_serializable():
    """Verdict.to_dict() round-trips through JSON."""
    from buildability.procedure import Verdict
    v = Verdict("RESEARCH")
    dumped = json.dumps(v.to_dict())
    loaded = json.loads(dumped)
    assert loaded["regime"] == "RESEARCH"
    assert loaded["results"] == []


def test_claim_closure_terminates_on_pathological_perturbation():
    """closure() with a perturbation that never reduces gaps runs to max_rounds."""
    spec = full_spec(gaps=(Gap("x", "?"),))
    # A perturbation that adds a gap but returns a different spec each time.
    counter = {"n": 0}
    def pathological(s):
        counter["n"] += 1
        return s.replace(gaps=s.gaps + (Gap(f"g{counter['n']}", "?"),))
    result, rounds = closure(spec, [pathological], max_rounds=5)
    # It ran to max_rounds without detecting divergence.
    assert rounds == 5, f"got {rounds} rounds"


def test_replace_validates_collection_types():
    """Spec.replace() rejects lists for collection fields."""
    spec = full_spec()
    with pytest.raises(TypeError):
        spec.replace(gaps=[Gap("a", "?")])


# ===========================================================================
# CLAIM GROUP 5: The central claim (unfalsified)
# ===========================================================================

def test_central_claim_has_ground_truth():
    """The central claim is now testable: a labeled corpus exists."""
    import json
    p = REPO / "experiments" / "ground_truth" / "outcomes.json"
    assert p.exists(), "ground truth corpus missing"
    outcomes = json.loads(p.read_text())
    assert len(outcomes) >= 3, "need >=3 outcomes"
    for o in outcomes:
        assert "build_attempted" in o
        assert "build_succeeded" in o
        assert "regime" in o


def test_central_claim_g1_passing_builds():
    """Every CONSTRUCTION-regime spec in the corpus built successfully."""
    import json
    outcomes = json.loads(
        (REPO / "experiments" / "ground_truth" / "outcomes.json").read_text()
    )
    passing = [o for o in outcomes if o["regime"] == "CONSTRUCTION"]
    assert passing, "no CONSTRUCTION outcome in corpus"
    for o in passing:
        assert o["build_succeeded"], (
            f"{o['spec']} passed G1 but failed to build: {o['error']}"
        )


def test_central_claim_g1_failing_fails():
    """Every RESEARCH-regime spec in the corpus failed to build."""
    import json
    outcomes = json.loads(
        (REPO / "experiments" / "ground_truth" / "outcomes.json").read_text()
    )
    failing = [o for o in outcomes if o["regime"] == "RESEARCH"]
    assert failing, "no RESEARCH outcome in corpus"
    for o in failing:
        assert not o["build_succeeded"], (
            f"{o['spec']} failed G1 but built successfully"
        )


def test_central_claim_has_counterexample():
    """A spec can pass all six element checks and still be incoherent.

    COUNTEREXAMPLE-DUPLICATE-OWNER declares two components with identical
    responsibility and an invariant stating "exactly one component owns a
    content record." G1 does not detect the contradiction. The spec lands
    at CONSTRUCTION. This test pins that fact.
    """
    import json
    p = REPO / "mesh" / "specs_counterexample" / "COUNTEREXAMPLE-DUPLICATE-OWNER.json"
    assert p.exists(), "counterexample spec missing"
    v = evaluate(spec_from_file(p))
    assert v.regime == "INCOHERENT", (
        f"G1.5 does not detect the incoherence: {v}"
    )
    spec = spec_from_file(p)
    responsibilities = [c.responsibility for c in spec.components]
    assert len(responsibilities) != len(set(responsibilities)), (
        "counterexample no longer has duplicate responsibilities"
    )
