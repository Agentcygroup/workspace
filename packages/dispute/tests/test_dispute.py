import pytest
from dispute import Dispute, DisputeState, File, Transition

def test_file_construction():
    f = File("a","b","claim","E-001".split(","))
    assert f.filer == "a"

def test_dispute_initial_state():
    d = Dispute(file=File("a","b","claim"))
    assert d.state == DisputeState.FILED
    assert d.case_id.startswith("DSP-")

def test_legal_transition():
    d = Dispute(file=File("a","b","c"))
    d.transition(DisputeState.UNDER_REVIEW, "reviewer")
    assert d.state == DisputeState.UNDER_REVIEW

def test_illegal_transition():
    d = Dispute(file=File("a","b","c"))
    with pytest.raises(ValueError):
        d.transition(DisputeState.RESOLVED, "x")

def test_unknown_state():
    d = Dispute(file=File("a","b","c"))
    with pytest.raises(ValueError):
        d.transition("nonsense","x")

def test_history_records():
    d = Dispute(file=File("a","b","c"))
    d.transition(DisputeState.UNDER_REVIEW,"r")
    d.transition(DisputeState.RESOLVED,"j")
    assert len(d.history) == 3
