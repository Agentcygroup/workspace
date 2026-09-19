"""SW: cross-domain assurance.

Two specs, one interface each, matching schema — composition succeeds.
Two specs, one interface each, conflicting schema — composition refuses.
That is what "cross-domain assurance" means in this repository: the
composition check runs across two specs, not within one.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import (
    Spec, Component, Interface, Invariant, Lifecycle, evaluate_many,
)


def _spec(name, ifaces):
    return Spec(
        name=name,
        components=(Component(f"{name}.api", "serve"),),
        interfaces=ifaces,
        invariants=(Invariant(f"{name}.lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
        substrate_available=True,
    )


def test_compose_accepts_matching():
    a = _spec("a", (Interface("auth", "openapi", "http", "v1", "5xx"),))
    b = _spec("b", (Interface("auth", "openapi", "http", "v1", "5xx"),))
    r = evaluate_many([a, b])
    assert r.ok is True, r.mismatches


def test_compose_refuses_conflicting_schema():
    a = _spec("a", (Interface("auth", "openapi", "http", "v1", "5xx"),))
    b = _spec("b", (Interface("auth", "graphql", "http", "v1", "5xx"),))
    r = evaluate_many([a, b])
    assert r.ok is False
    assert any(m.interface == "auth" for m in r.mismatches)


def test_compose_ignores_single_spec():
    a = _spec("a", (Interface("auth", "openapi", "http", "v1", "5xx"),))
    r = evaluate_many([a])
    assert r.ok is True
