import pytest
from gate import GATES, TRANSITIONS, GateMachine, GateError

def test_gates_count():
    assert len(GATES) == 6

def test_initial_state():
    m = GateMachine()
    assert m.state == "draft"
    assert not m.is_certified()

def test_full_chain():
    m = GateMachine()
    for g in GATES:
        m.sign(g, "someone")
    assert m.state == "H6_checked"
    m.sign("H5_certifying_officer","certifier")
    assert m.is_certified()

def test_out_of_order_raises():
    m = GateMachine()
    with pytest.raises(GateError):
        m.sign("H3_citation_verifier","x")

def test_unknown_gate_raises():
    m = GateMachine()
    with pytest.raises(GateError):
        m.sign("H9_fake","x")

def test_revoke():
    m = GateMachine()
    m.sign("H1_registry_curator","a")
    m.revoke("b")
    assert m.state == "revoked"

def test_history_length():
    m = GateMachine()
    m.sign("H1_registry_curator","a")
    assert len(m.history) == 2
