from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import Spec, Component, Interface, Invariant, Lifecycle, spec_distance


def _spec(name="x", comp="a", resp="serve", iface="rest", inv="lat"):
    return Spec(
        name=name,
        components=(Component(comp, resp),),
        interfaces=(Interface(iface, "openapi", "http", "v1", "5xx"),),
        invariants=(Invariant(inv, "p99<200ms"),),
        lifecycle=Lifecycle("a", "b", "c", "d", "e"),
        substrate="python",
        substrate_available=True,
    )


def test_identity():
    s = _spec()
    assert spec_distance(s, s) == 0.0


def test_symmetry():
    a = _spec(comp="a", resp="x")
    b = _spec(comp="b", resp="y")
    assert spec_distance(a, b) == spec_distance(b, a)


def test_range():
    a = _spec(comp="a", resp="x")
    b = _spec(comp="b", resp="y", iface="other", inv="other")
    d = spec_distance(a, b)
    assert 0.0 <= d <= 1.0


def test_triangle_inequality():
    a = _spec(comp="a")
    b = _spec(comp="b")
    c = _spec(comp="c")
    assert spec_distance(a, c) <= spec_distance(a, b) + spec_distance(b, c) + 1e-9


def test_increasing_distance():
    a = _spec(comp="a", resp="x")
    b1 = _spec(comp="a", resp="x", iface="other")
    b2 = _spec(comp="b", resp="y", iface="z", inv="other")
    assert spec_distance(a, b1) <= spec_distance(a, b2)
