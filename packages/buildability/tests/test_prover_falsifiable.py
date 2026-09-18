import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import Spec, Component, Interface, Invariant, Lifecycle
from buildability.models import MODEL_REGISTRY


def _spec():
    return Spec(
        name="x",
        components=(Component("api", "serve"),),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="boolean",
        substrate_available=True,
    )


def test_prover_can_fail():
    """The boolean model's prover must return False for a false candidate."""
    model = MODEL_REGISTRY["boolean"]
    spec = _spec()
    # A candidate that violates the spec's invariant predicate.
    candidate = {"latency": "p99>500ms"}
    result = model.prover(candidate, spec)
    assert result is False
