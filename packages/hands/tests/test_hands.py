from hands import validate_assignment, is_hand, is_archetype, is_function, is_state
from hands import HUMAN_HANDS, MACHINE_HANDS, ALL_HAND_KINDS
from hands.schema import build_all, schema

def test_all_hands_kinds_nonempty():
    assert len(HUMAN_HANDS) >= 30
    assert len(MACHINE_HANDS) >= 20
    assert "engineer" in HUMAN_HANDS
    assert "robot" in MACHINE_HANDS

def test_is_hand():
    assert is_hand("engineer")
    assert is_hand("ai_assistant")
    assert not is_hand("wizard")

def test_validate_minimal_ok():
    a = {
        "id": "W-1", "version": 1, "purpose": "demo", "outcome": "x",
        "beneficiary_refs": [], "originator_ref": "U-1",
        "accountable_owner_ref": "U-1", "performer_refs": [],
        "domain": "test", "scope": [], "jurisdictions": [],
        "functions": [], "authority": {}, "accountability": [],
        "required_competencies": [], "required_qualifications": [],
        "inputs": [], "assumptions": [], "constraints": [],
        "dependencies": [], "resources": [], "controls": [],
        "evidence_requirements": [], "acceptance_criteria": [],
        "measures": [], "risks": [], "stop_conditions": [],
        "escalation_paths": [], "state": "proposed",
    }
    assert validate_assignment(a) == []

def test_validate_missing_field():
    errs = validate_assignment({"id": "W-1"})
    assert any("missing field" in e for e in errs)

def test_validate_bad_state():
    a = {f: None for f in __import__("hands").REQUIRED_WORK_FIELDS}
    a["state"] = "nonexistent"
    errs = validate_assignment(a)
    assert any("unknown state" in e for e in errs)

def test_validate_bad_hand_kind():
    a = {f: [] for f in __import__("hands").REQUIRED_WORK_FIELDS}
    a["state"] = "proposed"
    a["performer_refs"] = [{"kind": "wizard"}]
    errs = validate_assignment(a)
    assert any("unknown hand kind" in e for e in errs)

def test_root_invariant_enforced():
    a = {f: [] for f in __import__("hands").REQUIRED_WORK_FIELDS}
    a["state"] = "proposed"
    a["identity_is_authority"] = True
    errs = validate_assignment(a)
    assert any("root invariant violated" in e for e in errs)

def test_build_all(tmp_path):
    written = build_all(tmp_path)
    assert any("human_hands" in w for w in written)
    assert any("work_assignment.schema" in w for w in written)
    import json
    s = json.loads((tmp_path / "work_assignment.schema.json").read_text())
    assert "state" in s["properties"]
