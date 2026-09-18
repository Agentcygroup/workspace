from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import (
    Spec, Component, Interface, Invariant, Lifecycle, Gap,
    diagnose,
)


def test_clean_spec_has_no_diagnostics():
    s = Spec(
        name="ok",
        components=(Component("api", "serve"),),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
        substrate_available=True,
    )
    assert diagnose(s) == ()


def test_missing_interfaces_diagnosed():
    s = Spec(
        name="x",
        components=(Component("api", "serve"),),
        interfaces=(),
        invariants=(Invariant("lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
        substrate_available=True,
    )
    ds = diagnose(s)
    assert any(d.element == "interfaces" and d.state == "empty" for d in ds)


def test_missing_components_diagnosed():
    s = Spec(
        name="x",
        components=(),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
        substrate_available=True,
    )
    ds = diagnose(s)
    assert any(d.element == "components" and d.state == "empty" for d in ds)


def test_open_gap_diagnosed():
    s = Spec(
        name="x",
        components=(Component("api", "serve"),),
        interfaces=(Interface("rest", "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant("lat", "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
        substrate_available=True,
        gaps=(Gap("ownership", "who owns?", resolved=False),),
    )
    ds = diagnose(s)
    assert any(d.element == "gaps" and "ownership" in d.hint for d in ds)
