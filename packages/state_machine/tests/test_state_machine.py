import pytest
from state_machine import Machine, TransitionError

def test_initial():
    m = Machine("a")
    assert m.state == "a"

def test_simple_transition():
    m = Machine("a").on("a","go","b")
    assert m.fire("go") == "b"

def test_unknown_event():
    m = Machine("a")
    with pytest.raises(TransitionError):
        m.fire("go")

def test_guard_blocks():
    m = Machine("a").on("a","go","b", guard=lambda c: False)
    with pytest.raises(TransitionError):
        m.fire("go")

def test_guard_allows():
    m = Machine("a").on("a","go","b", guard=lambda c: c.get("ok"))
    assert m.fire("go", {"ok": True}) == "b"

def test_effect_runs():
    hits = []
    m = Machine("a").on("a","go","b", effect=lambda c: hits.append(1))
    m.fire("go")
    assert hits == [1]

def test_history():
    m = Machine("a").on("a","go","b")
    m.fire("go")
    assert len(m.history) == 2
