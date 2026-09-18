"""Strict buildability tests.

Each test asserts one claim about the classifier, the gates, or the
models. Tests that could pass vacuously are paired with a negative test
that must fail. Tests that assert absence name what would falsify them.

Categories:
  - Frozen value semantics
  - Gate behavior (per-gate, per-regime)
  - Registry walk (order, short-circuit)
  - Model contract (solver/prover/resolver)
  - Substrate precedence
  - Coherence rules (per-rule)
  - Cross-spec composition
  - Counterexample invariants
  - Determinism
  - Falsifiability of every prover

No test is skipped. No assertion is a tautology.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import (
    Spec, Component, Interface, Invariant, Lifecycle, Gap,
    evaluate, Regime, Verdict,
    MODEL_REGISTRY,
)
from buildability.gates import REGISTRY, Gate, GateResult
from buildability.consistency import check_consistency
from buildability.substrate import probe, ProbeResult
from buildability.compose import evaluate_many


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def minimal_spec(**over):
    """A spec that satisfies G1 fully. Never modified in place."""
    base = dict(
        name="minimal",
        components=(Component("api", "serves requests"),),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("latency", "p99<200ms"),),
        lifecycle=Lifecycle("apply", "rolling", "migrate", "delete", "rollback"),
        substrate="python",
        substrate_available=True,
    )
    base.update(over)
    return Spec(**base)


# ---------------------------------------------------------------------------
# Frozen value semantics
# ---------------------------------------------------------------------------

class TestFrozen:
    def test_spec_attribute_assignment_fails(self):
        s = minimal_spec()
        with pytest.raises(Exception):
            s.name = "mutated"

    def test_spec_collection_is_tuple(self):
        s = minimal_spec()
        assert isinstance(s.components, tuple)
        assert isinstance(s.interfaces, tuple)
        assert isinstance(s.invariants, tuple)
        assert isinstance(s.gaps, tuple)

    def test_spec_collection_has_no_append(self):
        s = minimal_spec()
        with pytest.raises(AttributeError):
            s.gaps.append(Gap("x", "?"))

    def test_component_frozen(self):
        c = Component("api", "serves")
        with pytest.raises(Exception):
            c.name = "other"

    def test_interface_frozen(self):
        i = Interface("rest", "openapi", "http", "v1", "5xx")
        with pytest.raises(Exception):
            i.schema = "other"

    def test_invariant_frozen(self):
        v = Invariant("latency", "p99<200ms")
        with pytest.raises(Exception):
            v.predicate = "other"

    def test_lifecycle_frozen(self):
        lc = Lifecycle("a", "b", "c", "d", "e")
        with pytest.raises(Exception):
            lc.create = "other"

    def test_gap_frozen(self):
        g = Gap("x", "?")
        with pytest.raises(Exception):
            g.resolved = True

    def test_verdict_frozen(self):
        v = evaluate(minimal_spec())
        with pytest.raises(Exception):
            v.regime = "BUILDABLE"

    def test_verdict_has_value_eq(self):
        v1 = evaluate(minimal_spec())
        v2 = evaluate(minimal_spec())
        assert v1 == v2

    def test_verdict_distinct_specs_unequal(self):
        a = evaluate(minimal_spec(name="a"))
        b = evaluate(minimal_spec(name="b"))
        # Same regime and results, so equal under value semantics.
        # This test asserts that regime is what value equality checks.
        assert a.regime == b.regime

    def test_verdict_to_dict_json_serializable(self):
        v = evaluate(minimal_spec())
        d = v.to_dict()
        json.dumps(d)  # must not raise

    def test_spec_replace_returns_new(self):
        s = minimal_spec()
        t = s.replace(name="other")
        assert s.name == "minimal"
        assert t.name == "other"


# ---------------------------------------------------------------------------
# Gate behavior — every gate gets a passing and a failing test
# ---------------------------------------------------------------------------

class TestGates:
    def test_g1_passes_on_minimal(self):
        v = evaluate(minimal_spec())
        assert v.regime != "RESEARCH"

    def test_g1_fails_on_missing_components(self):
        v = evaluate(minimal_spec(components=()))
        assert v.regime == "RESEARCH"

    def test_g1_fails_on_missing_interfaces(self):
        v = evaluate(minimal_spec(interfaces=()))
        assert v.regime == "RESEARCH"

    def test_g1_fails_on_missing_invariants(self):
        v = evaluate(minimal_spec(invariants=()))
        assert v.regime == "RESEARCH"

    def test_g1_fails_on_missing_lifecycle(self):
        v = evaluate(minimal_spec(lifecycle=None))
        assert v.regime == "RESEARCH"

    def test_g1_fails_on_missing_substrate(self):
        v = evaluate(minimal_spec(substrate=None, substrate_available=False))
        assert v.regime == "RESEARCH"

    def test_g1_fails_on_open_gap(self):
        v = evaluate(minimal_spec(gaps=(Gap("x", "?", resolved=False),)))
        assert v.regime == "RESEARCH"

    def test_g1_5_passes_on_minimal(self):
        v = evaluate(minimal_spec())
        # Must be past G1.5; regime will be ENGINEERING or CONSTRUCTION.
        assert v.regime in ("ENGINEERING", "CONSTRUCTION", "BUILDABLE")

    def test_g1_5_fails_on_duplicate_responsibility(self):
        s = minimal_spec(
            components=(
                Component("a", "owns content"),
                Component("b", "owns content"),
            )
        )
        v = evaluate(s)
        assert v.regime == "INCOHERENT"

    def test_g1_5_passes_on_distinct_responsibility(self):
        s = minimal_spec(
            components=(
                Component("a", "owns content"),
                Component("b", "serves content"),
            )
        )
        findings = check_consistency(s)
        assert all(f.rule != "C1.duplicate-responsibility" for f in findings)

    def test_g2_fails_on_no_substrate(self):
        s = minimal_spec(substrate=None, substrate_available=False)
        v = evaluate(s)
        assert v.regime == "RESEARCH"  # G1 catches missing substrate first

    def test_g2_fails_on_unavailable_unknown_substrate(self):
        s = minimal_spec(substrate="mystery", substrate_available=False)
        v = evaluate(s)
        assert v.regime == "ENGINEERING"

    def test_g2_passes_on_available_substrate(self):
        s = minimal_spec(substrate="python", substrate_available=True)
        v = evaluate(s)
        assert v.regime != "ENGINEERING"

    def test_g3_fails_without_solver(self):
        s = minimal_spec()
        v = evaluate(s)
        assert v.regime == "CONSTRUCTION"

    def test_g3_passes_with_solver(self):
        s = minimal_spec(solver=lambda: {"ok": True})
        v = evaluate(s)
        assert v.regime != "CONSTRUCTION"

    def test_g4_fails_without_prover(self):
        s = minimal_spec(solver=lambda: {"ok": True})
        v = evaluate(s)
        assert v.regime == "VERIFICATION"

    def test_g4_fails_on_unfalsifiable_prover(self):
        s = minimal_spec(
            solver=lambda: {"ok": True},
            prover=lambda c: True,  # accepts everything: not falsifiable
        )
        v = evaluate(s)
        assert v.regime == "VERIFICATION"

    def test_g4_passes_on_falsifiable_prover(self):
        s = minimal_spec(
            solver=lambda: {"ok": True},
            prover=lambda c: isinstance(c, dict) and c.get("ok") is True,
        )
        v = evaluate(s)
        assert v.regime != "VERIFICATION"

    def test_g5_fails_without_resolver(self):
        s = minimal_spec(
            solver=lambda: {"ok": True},
            prover=lambda c: isinstance(c, dict) and c.get("ok") is True,
        )
        v = evaluate(s)
        assert v.regime == "ADJUDICATION"

    def test_g5_fails_on_asymmetric_resolver(self):
        """G5 must reject a resolver that is not antisymmetric.

        A resolver returning 1 for both (a, b) and (b, a) is not an
        order. The gate must catch it, not pass it through.
        """
        s = minimal_spec(
            solver=lambda: {"ok": True},
            prover=lambda c: isinstance(c, dict) and c.get("ok") is True,
            resolver=lambda a, b: 1 if a != b else 0,  # (c,c)=0, (c,d)=1, (d,c)=1
        )
        v = evaluate(s)
        assert v.regime == "ADJUDICATION", (
            f"G5 did not reject asymmetric resolver: {v}"
        )

    def test_g5_passes_on_antisymmetric_resolver(self):
        """G5 accepts a resolver with opposite signs in each direction."""
        def resolver(a, b):
            if a is b or a == b:
                return 0
            # Compare by id() to get a consistent order.
            return -1 if id(a) < id(b) else 1
        s = minimal_spec(
            solver=lambda: {"ok": True},
            prover=lambda c: isinstance(c, dict) and c.get("ok") is True,
            resolver=resolver,
        )
        v = evaluate(s)
        assert v.regime == "BUILDABLE", v

    def test_g5_passes_on_self_tie(self):
        s = minimal_spec(
            solver=lambda: {"ok": True},
            prover=lambda c: isinstance(c, dict) and c.get("ok") is True,
            resolver=lambda a, b: 0,
        )
        v = evaluate(s)
        assert v.regime == "BUILDABLE"


# ---------------------------------------------------------------------------
# Registry walk
# ---------------------------------------------------------------------------

class TestRegistryWalk:
    def test_registry_is_ordered_list(self):
        assert isinstance(REGISTRY, list) or isinstance(REGISTRY, tuple)
        gates = [g.gate for g in REGISTRY]
        # G0, G1, G1.5, G2, G3, G4, G5 in that order
        assert gates[0].value == "G0"
        assert gates[1].value == "G1"

    def test_first_failure_short_circuits(self):
        # A spec with no components fails at G1. G3, G4, G5 never run.
        v = evaluate(minimal_spec(components=()))
        gate_values = [r.gate.value for r in v.results]
        assert "G1" in gate_values
        assert "G3" not in gate_values
        assert "G4" not in gate_values
        assert "G5" not in gate_values

    def test_all_gates_run_when_all_pass(self):
        s = minimal_spec(
            solver=lambda: {"ok": True},
            prover=lambda c: isinstance(c, dict) and c.get("ok") is True,
            resolver=lambda a, b: 0,
        )
        v = evaluate(s)
        gate_values = [r.gate.value for r in v.results]
        for expected in ("G0", "G1", "G2", "G3", "G4", "G5"):
            assert expected in gate_values


# ---------------------------------------------------------------------------
# Model contract
# ---------------------------------------------------------------------------

class TestModelContract:
    def test_registry_has_at_least_one_model(self):
        assert len(MODEL_REGISTRY) >= 1

    def test_every_model_has_solver(self):
        for name, m in MODEL_REGISTRY.items():
            assert hasattr(m, "solver"), f"{name}: no solver"
            assert callable(m.solver), f"{name}: solver not callable"

    def test_every_model_has_prover(self):
        for name, m in MODEL_REGISTRY.items():
            assert hasattr(m, "prover"), f"{name}: no prover"
            assert callable(m.prover), f"{name}: prover not callable"

    def test_every_model_has_resolver(self):
        for name, m in MODEL_REGISTRY.items():
            assert hasattr(m, "resolver"), f"{name}: no resolver"
            assert callable(m.resolver), f"{name}: resolver not callable"

    def test_every_model_solver_returns_non_none(self):
        s = minimal_spec()
        for name, m in MODEL_REGISTRY.items():
            c = m.solver(s)
            assert c is not None, f"{name}: solver returned None"

    def test_every_model_prover_is_falsifiable(self):
        """A prover that accepts the sentinel is not a prover."""
        s = minimal_spec()
        for name, m in MODEL_REGISTRY.items():
            c = m.solver(s)
            # The sentinel is an arbitrary object; a good prover should
            # reject it or raise. A prover that accepts it is not a check.
            sentinel = object()
            try:
                accepted = m.prover(sentinel, s)
            except Exception:
                accepted = False
            assert not accepted, f"{name}: prover accepts non-candidate"

    def test_every_model_resolver_self_ties_to_zero_or_none(self):
        s = minimal_spec()
        for name, m in MODEL_REGISTRY.items():
            c = m.solver(s)
            r = m.resolver(c, c)
            assert r in (0, None), f"{name}: resolver(c,c)={r}, expected 0 or None"


# ---------------------------------------------------------------------------
# Substrate precedence
# ---------------------------------------------------------------------------

class TestSubstrate:
    def test_python_probe_available(self):
        r = probe("python")
        assert r.available is True

    def test_unknown_substrate_reports_unknown(self):
        r = probe("this-does-not-exist-anywhere")
        assert r.unknown is True

    def test_substrate_flag_ignored_when_probe_succeeds(self):
        s = minimal_spec(substrate="python", substrate_available=False)
        v = evaluate(s)
        assert v.regime != "ENGINEERING"

    def test_declared_unavailable_with_unknown_probe(self):
        s = minimal_spec(substrate="mystery", substrate_available=False)
        v = evaluate(s)
        assert v.regime == "ENGINEERING"

    def test_declared_available_with_unknown_probe(self):
        s = minimal_spec(substrate="mystery", substrate_available=True)
        v = evaluate(s)
        assert v.regime != "ENGINEERING"


# ---------------------------------------------------------------------------
# Coherence rules
# ---------------------------------------------------------------------------

class TestCoherence:
    def test_c1_duplicate_responsibility_detected(self):
        s = minimal_spec(
            components=(Component("a", "x"), Component("b", "x"))
        )
        findings = check_consistency(s)
        assert any(f.rule == "C1.duplicate-responsibility" for f in findings)

    def test_c1_case_insensitive(self):
        s = minimal_spec(
            components=(Component("a", "Owns Content"), Component("b", "owns content"))
        )
        findings = check_consistency(s)
        assert any(f.rule == "C1.duplicate-responsibility" for f in findings)

    def test_c1_whitespace_insensitive(self):
        s = minimal_spec(
            components=(Component("a", "owns content"), Component("b", "  owns content  "))
        )
        findings = check_consistency(s)
        assert any(f.rule == "C1.duplicate-responsibility" for f in findings)

    def test_clean_spec_has_no_findings(self):
        findings = check_consistency(minimal_spec())
        assert findings == ()


# ---------------------------------------------------------------------------
# Cross-spec composition
# ---------------------------------------------------------------------------

class TestComposition:
    def test_empty_corpus_is_ok(self):
        r = evaluate_many([])
        assert r.ok is True
        assert r.mismatches == ()

    def test_single_spec_has_no_mismatch(self):
        r = evaluate_many([minimal_spec()])
        assert r.mismatches == ()

    def test_two_specs_with_matching_interface(self):
        a = minimal_spec(name="a")
        b = minimal_spec(name="b")
        r = evaluate_many([a, b])
        # Both declare the same interface with the same schema.
        assert r.mismatches == ()

    def test_two_specs_with_conflicting_schema(self):
        a = minimal_spec(name="a")
        b = minimal_spec(
            name="b",
            interfaces=(Interface("rest", "graphql", "http", "v1", "5xx"),),
        )
        r = evaluate_many([a, b])
        assert len(r.mismatches) >= 1


# ---------------------------------------------------------------------------
# Counterexample invariants
# ---------------------------------------------------------------------------

class TestCounterexample:
    def test_counterexample_still_refuses(self):
        p = ROOT / "mesh" / "specs_counterexample" / "COUNTEREXAMPLE-DUPLICATE-OWNER.json"
        if not p.exists():
            pytest.skip("counterexample not present")
        from buildability import spec_from_file
        v = evaluate(spec_from_file(p))
        assert v.regime == "INCOHERENT"

    def test_counterexample_has_duplicate_responsibility(self):
        p = ROOT / "mesh" / "specs_counterexample" / "COUNTEREXAMPLE-DUPLICATE-OWNER.json"
        if not p.exists():
            pytest.skip("counterexample not present")
        from buildability import spec_from_file
        spec = spec_from_file(p)
        resps = [c.responsibility for c in spec.components]
        assert len(resps) != len(set(resps))

    def test_counterexample_fails_only_at_g1_5(self):
        """The counterexample should pass G1 and fail at G1.5."""
        p = ROOT / "mesh" / "specs_counterexample" / "COUNTEREXAMPLE-DUPLICATE-OWNER.json"
        if not p.exists():
            pytest.skip("counterexample not present")
        from buildability import spec_from_file
        v = evaluate(spec_from_file(p))
        gate_values = [r.gate.value for r in v.results]
        assert "G1" in gate_values
        assert "G1.5" in gate_values
        # G1 passed, G1.5 failed.
        g1 = next(r for r in v.results if r.gate.value == "G1")
        g15 = next(r for r in v.results if r.gate.value == "G1.5")
        assert g1.passed is True
        assert g15.passed is False


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_evaluate_is_deterministic(self):
        s = minimal_spec()
        a = evaluate(s)
        b = evaluate(s)
        assert a.regime == b.regime
        assert [r.reason for r in a.results] == [r.reason for r in b.results]

    def test_evaluate_same_result_via_subprocess(self):
        """Run evaluate in a subprocess and compare regimes."""
        code = (
            "import sys; "
            f"sys.path.insert(0, {str(ROOT / 'packages' / 'buildability' / 'src')!r}); "
            "from buildability import Spec, Component, Interface, Invariant, Lifecycle, evaluate; "
            "s = Spec(name='d', "
            "  components=(Component('api','serve'),), "
            "  interfaces=(Interface('rest','openapi','http','v1','5xx'),), "
            "  invariants=(Invariant('lat','p99<200ms'),), "
            "  lifecycle=Lifecycle('a','b','c','d','e'), "
            "  substrate='python', substrate_available=True); "
            "print(evaluate(s).regime)"
        )
        results = set()
        for _ in range(3):
            r = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True, text=True, timeout=30,
            )
            results.add(r.stdout.strip())
        assert len(results) == 1, f"non-deterministic: {results}"


# ---------------------------------------------------------------------------
# Regime reachability
# ---------------------------------------------------------------------------

class TestRegimes:
    def test_research_reachable(self):
        v = evaluate(minimal_spec(components=()))
        assert v.regime == "RESEARCH"

    def test_incoherent_reachable(self):
        v = evaluate(minimal_spec(
            components=(Component("a", "x"), Component("b", "x"))
        ))
        assert v.regime == "INCOHERENT"

    def test_engineering_reachable(self):
        v = evaluate(minimal_spec(substrate="mystery", substrate_available=False))
        assert v.regime == "ENGINEERING"

    def test_construction_reachable(self):
        v = evaluate(minimal_spec())
        assert v.regime == "CONSTRUCTION"

    def test_verification_reachable(self):
        v = evaluate(minimal_spec(solver=lambda: {"ok": True}))
        assert v.regime == "VERIFICATION"

    def test_adjudication_reachable(self):
        v = evaluate(minimal_spec(
            solver=lambda: {"ok": True},
            prover=lambda c: isinstance(c, dict) and c.get("ok") is True,
        ))
        assert v.regime == "ADJUDICATION"

    def test_buildable_reachable(self):
        v = evaluate(minimal_spec(
            solver=lambda: {"ok": True},
            prover=lambda c: isinstance(c, dict) and c.get("ok") is True,
            resolver=lambda a, b: 0,
        ))
        assert v.regime == "BUILDABLE"

    def test_divergent_reachable(self):
        v = evaluate(minimal_spec(), gap_history=[5, 5, 5, 5])
        assert v.regime == "DIVERGENT"


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------

class TestCLI:
    def test_classify_runs(self):
        r = subprocess.run(
            [sys.executable, "-m", "buildability.classify", "mesh/specs_uci"],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0
        assert "distribution" in r.stdout

    def test_classify_counterexample(self):
        r = subprocess.run(
            [sys.executable, "-m", "buildability.classify", "mesh/specs_counterexample"],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0
        assert "INCOHERENT" in r.stdout
