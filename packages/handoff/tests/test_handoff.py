import pytest
from handoff import Handoff, Mode, HandoffState

def test_valid_handoff():
    h = Handoff("a","b", Mode.ASSIGNMENT, "OBJ-1")
    assert h.state == HandoffState.PROPOSED

def test_bad_mode():
    with pytest.raises(ValueError):
        Handoff("a","b","nonsense","OBJ-1")

def test_accept():
    h = Handoff("a","b", Mode.ASSIGNMENT, "OBJ-1")
    h.accept()
    assert h.state == HandoffState.ACCEPTED

def test_accept_twice_fails():
    h = Handoff("a","b", Mode.ASSIGNMENT, "OBJ-1")
    h.accept()
    with pytest.raises(ValueError):
        h.accept()

def test_reject():
    h = Handoff("a","b", Mode.REVIEW, "OBJ-1")
    h.reject()
    assert h.state == HandoffState.REJECTED

def test_modes_closed():
    assert len(Mode.ALL) == 5
