import pytest
from kernel.envelope import make_envelope, verify_envelope, ENVELOPE_VERSION
from kernel.operators import OPERATORS, apply_operator, denotation
from kernel.axioms import AXIOMS, check_axiom, independence_report
from kernel.mappings import MAPPINGS, map_envelope, preservation_report
from kernel.sandbox import run_in_sandbox, SandboxRejection
from kernel.domains import physics, biology

def test_ten_operators():
    assert len(OPERATORS) == 10
    for name in OPERATORS:
        assert denotation(name)

def test_operators_id_and_neg():
    assert apply_operator("id", 5) == 5
    assert apply_operator("neg", True) is False

def test_operator_merge_split():
    assert apply_operator("merge", [[1,2],[3]]) == [1,2,3]
    assert apply_operator("split", [1,2,3,4], 2) == [[1,2],[3,4]]

def test_operator_align():
    a = {"x":1,"y":2}; b = {"y":3,"z":4}
    assert apply_operator("align", a, b) == {"y": (2,3)}

def test_operator_project():
    assert apply_operator("project", ["a"], {"a":1,"b":2}) == {"a":1}

def test_eight_axioms():
    assert len(AXIOMS) == 8

def test_envelope_verify_ok():
    e = make_envelope("E-1","physics","observable.v1",{"x":1},units={"x":"m"},provenance=["obs"])
    assert verify_envelope(e) == []
    assert e.schema_version == ENVELOPE_VERSION

def test_axioms_satisfied_on_good_envelope():
    e = make_envelope("E-2","physics","observable.v1",{"x":1},units={"x":"m"},provenance=["obs"])
    r = independence_report(e)
    assert len(r["satisfied"]) == 8
    assert r["violated"] == {}

def test_mappings_three():
    assert len(MAPPINGS) == 3
    for name, m in MAPPINGS.items():
        assert m["preserved"]
        assert m["rationale"]

def test_map_physics_to_biology():
    e = make_envelope("E-3","physics","observable.v1",{"units":"m"},units={"x":"m"},provenance=["obs"])
    m = map_envelope(e, "physics_to_biology")
    assert m.domain == "biology"
    assert "units" in m.preserved
    assert "mapped:physics_to_biology" in m.provenance

def test_map_wrong_domain_raises():
    e = make_envelope("E-4","biology","trait.v1",{},provenance=["obs"])
    with pytest.raises(ValueError):
        map_envelope(e, "physics_to_biology")

def test_sandbox_allows_known_operator():
    r = run_in_sandbox("id", (5,))
    assert r["result"] == 5
    assert "signature" in r

def test_sandbox_rejects_unknown_operator():
    with pytest.raises(SandboxRejection):
        run_in_sandbox("evil", (1,))

def test_sandbox_rejects_oversized_payload():
    huge = ["x" * 1000] * 2000
    with pytest.raises(SandboxRejection):
        run_in_sandbox("id", (huge,))

def test_physics_adapter():
    e = physics.emit("P-1","mass",9.81,"kg",provenance=["lab"])
    assert e.domain == "physics"
    assert e.units == {"mass":"kg"}
    assert verify_envelope(e) == []

def test_biology_adapter():
    e = biology.emit("B-1","Homo sapiens","height_cm",175.0,provenance=["field"])
    assert e.domain == "biology"
    assert verify_envelope(e) == []
