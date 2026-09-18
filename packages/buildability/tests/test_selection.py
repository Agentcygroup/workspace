from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import (
    Spec, Component, Interface, Invariant, Lifecycle,
    select_model, NoSuitableModel, MODEL_REGISTRY,
)


def _spec(**over):
    base = dict(
        name="x",
        components=(Component("api", "serve"),),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
        substrate_available=True,
    )
    base.update(over)
    return Spec(**base)


def test_substrate_names_model():
    assert select_model(_spec(substrate="boolean")) == "boolean"


def test_internal_protocol_selects_pi():
    s = _spec(interfaces=(Interface("rest", "openapi", "internal", "v1", "5xx"),))
    assert select_model(s) == "pi"


def test_state_machine_selects_general():
    s = _spec(components=(Component("state_machine", "manages state"),))
    assert select_model(s) == "general"


def test_fallback_to_boolean():
    assert select_model(_spec()) == "boolean"


def test_no_discriminating_feature_raises():
    s = _spec(components=(), interfaces=())
    with pytest.raises(NoSuitableModel):
        select_model(s)


def test_every_selection_is_in_registry():
    for sub in list(MODEL_REGISTRY):
        s = _spec(substrate=sub)
        assert select_model(s) == sub
