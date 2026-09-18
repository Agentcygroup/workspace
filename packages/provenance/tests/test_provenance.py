import pytest
from provenance import Entity, Activity, Agent, Chain

def test_chain_empty():
    c = Chain()
    assert c.to_dict()["activities"] == []

def test_add_entity_agent_activity():
    c = Chain()
    a = Agent("alice","human")
    e1 = Entity("E1","h1")
    e2 = Entity("E2","h2")
    c.add_agent(a); c.add_entity(e1); c.add_entity(e2)
    act = Activity("A1", agent=a, used=["E1"], generated=["E2"])
    c.add_activity(act)
    assert len(c.activities) == 1

def test_unknown_used():
    c = Chain()
    with pytest.raises(ValueError):
        c.add_activity(Activity("A1", used=["missing"]))

def test_unknown_agent():
    c = Chain()
    with pytest.raises(ValueError):
        c.add_activity(Activity("A1", agent=Agent("ghost")))

def test_to_dict_shape():
    c = Chain()
    d = c.to_dict()
    assert set(d.keys()) == {"activities","entities","agents"}
