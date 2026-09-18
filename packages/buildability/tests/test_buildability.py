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


def test_g2_unavailable():
    r = g2_substrate(_full_spec(substrate_available=False))
    assert not r.passed


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
    v = evaluate(_full_spec(substrate_available=False))
    assert v.regime == Regime.ENGINEERING


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


def test_l1_no_substrate_routes_to_engineering():
    """A spec with no substrate must fail G2, not silently pass to G3."""
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
    v = evaluate(spec)
    assert v.regime == Regime.ENGINEERING, v
