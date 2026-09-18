import pytest
from buildability import (
    Spec, Component, Interface, Invariant, Lifecycle, Gap,
    g0_convergence, g1_spec, g2_substrate, g3_solver, g4_prover, g5_resolver,
    evaluate, Regime, is_fixed_point,
)


def _full_spec(**over):
    base = dict(
        name="demo",
        components=[Component("api", "serves requests")],
        interfaces=[Interface("rest", "openapi", "http", "v1", "5xx on failure")],
        invariants=[Invariant("latency", "p99 < 200ms", check=lambda c: True)],
        lifecycle=Lifecycle("apply", "rolling", "migrate", "delete", "rollback"),
        substrate="kubernetes",
        substrate_available=True,
        gaps=[],
    )
    base.update(over)
    return Spec(**base)


def test_g1_complete():
    assert g1_spec(_full_spec()).passed


def test_g1_missing_component():
    r = g1_spec(_full_spec(components=[]))
    assert not r.passed
    assert "components" in r.reason


def test_g1_open_gap_blocks():
    r = g1_spec(_full_spec(gaps=[Gap("ownership", "who owns content?", resolved=False)]))
    assert not r.passed
    assert "ownership" in r.reason


def test_g2_missing_substrate():
    r = g2_substrate(_full_spec(substrate=None))
    assert not r.passed


def test_g2_flag_ignored_when_probe_succeeds():
    """Probe wins. A spec cannot deny an available substrate.

    This is the design decision made in _g2: the environment answers
    availability better than the spec author. substrate_available is
    only consulted when the probe has no information.
    """
    r = g2_substrate(_full_spec(substrate="local", substrate_available=False))
    assert r.passed, r.reason


def test_g3_no_solver():
    r, c = g3_solver(_full_spec())
    assert not r.passed and c is None


def test_g3_solver_returns_candidate():
    r, c = g3_solver(_full_spec(solver=lambda: {"ok": True}))
    assert r.passed and c == {"ok": True}


def test_g4_no_prover():
    assert not g4_prover(_full_spec(), "c").passed


def test_g4_falsifiable_prover():
    # Prover that accepts dicts and rejects everything else.
    p = lambda c: isinstance(c, dict) and c.get("ok") is True
    assert g4_prover(_full_spec(prover=p), {"ok": True}).passed


def test_g4_unfalsifiable_prover_rejected():
    # Prover that always returns True is not a prover.
    p = lambda c: True
    r = g4_prover(_full_spec(prover=p), "anything")
    assert not r.passed
    assert "falsifiable" in r.reason


def test_g5_no_resolver():
    assert not g5_resolver(_full_spec(), "c").passed


def test_g5_self_tie_ok():
    # Resolver that returns 0 for identical candidates.
    r = lambda a, b: 0
    assert g5_resolver(_full_spec(resolver=r), "c").passed


def test_evaluate_buildable():
    p = lambda c: isinstance(c, dict)
    r = lambda a, b: 0
    v = evaluate(_full_spec(solver=lambda: {"ok": True}, prover=p, resolver=r))
    assert v.regime == Regime.BUILDABLE


def test_evaluate_divergent():
    v = evaluate(_full_spec(), gap_history=[5, 5, 5, 5])
    assert v.regime == Regime.DIVERGENT


def test_evaluate_research():
    v = evaluate(_full_spec(gaps=[Gap("x", "?", resolved=False)]))
    assert v.regime == Regime.RESEARCH


def test_evaluate_engineering():
    """ENGINEERING requires an unavailable substrate, not just a flag.

    To reach ENGINEERING the probe must actually fail. We use a
    substrate name with no registered probe and substrate_available=False
    so the probe returns unknown and the flag decides.
    """
    v = evaluate(_full_spec(substrate="mystery-substrate", substrate_available=False))
    assert v.regime == Regime.ENGINEERING, v


def test_evaluate_construction():
    v = evaluate(_full_spec())
    assert v.regime == Regime.CONSTRUCTION


def test_evaluate_verification():
    v = evaluate(_full_spec(solver=lambda: "c"))
    assert v.regime == Regime.VERIFICATION


def test_evaluate_adjudication():
    p = lambda c: isinstance(c, dict)
    v = evaluate(_full_spec(solver=lambda: {"ok": True}, prover=p))
    assert v.regime == Regime.ADJUDICATION


def test_fixed_point():
    spec = _full_spec(solver=lambda: 42)
    # Perturbations that do not change the output.
    perturbs = [
        lambda s: Spec(**{**s.__dict__, "name": s.name + "-x"}),
        lambda s: Spec(**{**s.__dict__, "substrate": (s.substrate or "") + "-y"}),
    ]
    assert is_fixed_point(spec, perturbs)


def test_no_substrate_is_research_not_engineering():
    """Substrate is a spec element, not a runtime property.

    A spec that does not name its substrate is INCOMPLETE (G1 fails,
    regime RESEARCH). A spec that names a substrate which is unavailable
    fails G2 (regime ENGINEERING). The two are different problems.
    """
    from buildability.loader import spec_from_dict
    raw = {
        "kind_id": "NO-SUB",
        "components": [{"name": "api", "responsibility": "serve"}],
        "interfaces": [{"name": "rest", "schema": "openapi", "protocol": "http",
                        "version": "v1", "failure_semantics": "5xx"}],
        "invariants": [{"name": "latency", "predicate": "p99<200ms"}],
        "lifecycle": {"create": "a", "update": "b", "migrate": "c",
                      "delete": "d", "rollback": "e"},
        # no 'level', no 'substrate'
    }
    spec = spec_from_dict(raw)
    assert spec.substrate is None
    assert spec.substrate_available is False

    # No substrate named -> spec is incomplete -> RESEARCH.
    v = evaluate(spec)
    assert v.regime == Regime.RESEARCH, v
    assert any("substrate" in r.reason for r in v.results if not r.passed)


def test_declared_but_unavailable_substrate_is_engineering():
    """A spec declaring an unknown substrate as unavailable fails G2.

    The probe returns unknown for unregistered substrate names. In that
    case the spec's flag decides. substrate_available=False with no
    probe means the spec author has spoken and the framework honors it.
    """
    from buildability.model import Spec, Component, Interface, Invariant, Lifecycle
    spec = Spec(
        name="HAS-SUB-NO-AVAIL",
        components=(Component("api", "serve"),),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("latency", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="mystery-substrate",
        substrate_available=False,
    )
    v = evaluate(spec)
    assert v.regime == Regime.ENGINEERING, v
    assert any("declared unavailable" in r.reason
               for r in v.results if not r.passed)

def test_spec_is_frozen():
    """Spec must reject attribute assignment at runtime."""
    spec = _full_spec()
    try:
        spec.name = "mutated"
    except Exception as e:
        # dataclasses.FrozenInstanceError is the expected type.
        assert "frozen" in type(e).__name__.lower() or "cannot assign" in str(e).lower()
    else:
        raise AssertionError("Spec accepted mutation; frozen contract broken")


def test_gap_is_frozen():
    """Gap is a value object; mutating `resolved` must fail."""
    from buildability.model import Gap
    g = Gap("x", "?", resolved=False)
    try:
        g.resolved = True
    except Exception:
        pass
    else:
        raise AssertionError("Gap accepted mutation; frozen contract broken")


def test_closure_does_not_mutate_input():
    """closure must return a new spec and leave the input unchanged."""
    from buildability.fixedpoint import closure

    base = _full_spec(solver=lambda: 42)
    # A perturbation that closes no gaps and produces an equal spec.
    def noop(s):
        return s

    before_name = base.name
    before_gaps = len(base.gaps)
    result, rounds = closure(base, [noop], max_rounds=10)

    # Input is untouched.
    assert base.name == before_name
    assert len(base.gaps) == before_gaps
    # Output is either the same object (identity) or structurally equal.
    assert result == base or result is base

def test_g0_no_history_passes():
    """G0 with no history is vacuously true."""
    from buildability.gates import g0_convergence
    r = g0_convergence([])
    assert r.passed
    assert "insufficient" in r.reason


def test_g0_divergent_fails():
    """G0 fails when the gap count does not strictly decrease."""
    from buildability.gates import g0_convergence
    r = g0_convergence([5, 5, 5, 5])
    assert not r.passed
    assert "divergent" in r.reason


def test_g0_convergent_passes():
    """G0 passes when the gap count strictly decreases each iteration."""
    from buildability.gates import g0_convergence
    r = g0_convergence([5, 4, 3, 2, 1, 0])
    assert r.passed


def test_g1_5_duplicate_responsibility_detected():
    """G1.5 catches components with identical responsibility."""
    from buildability.consistency import check_consistency
    from buildability.model import (
        Spec, Component, Interface, Invariant, Lifecycle,
    )
    spec = Spec(
        name="dup",
        components=(
            Component("a", "owns content"),
            Component("b", "owns content"),
        ),
        interfaces=(Interface("x", "s", "p", "v", "f"),),
        invariants=(Invariant("i", "p"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
        substrate_available=True,
    )
    findings = check_consistency(spec)
    assert any(f.rule == "C1.duplicate-responsibility" for f in findings)


def test_g1_5_clean_spec_passes():
    """G1.5 passes a spec whose components have distinct responsibilities."""
    from buildability.consistency import check_consistency
    from buildability.model import (
        Spec, Component, Interface, Invariant, Lifecycle,
    )
    spec = Spec(
        name="clean",
        components=(
            Component("a", "owns content"),
            Component("b", "serves content"),
        ),
        interfaces=(Interface("x", "s", "p", "v", "f"),),
        invariants=(Invariant("i", "p"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
        substrate_available=True,
    )
    findings = check_consistency(spec)
    assert findings == ()
