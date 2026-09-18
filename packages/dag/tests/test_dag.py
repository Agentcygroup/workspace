import pytest
from dag import DAG, CycleError

def test_empty():
    assert DAG().topo() == []

def test_linear():
    g = DAG()
    g.add_edge("a","b"); g.add_edge("b","c")
    assert g.topo() == ["a","b","c"]

def test_diamond():
    g = DAG()
    for a,b in [("a","b"),("a","c"),("b","d"),("c","d")]:
        g.add_edge(a,b)
    order = g.topo()
    assert order.index("a") < order.index("b") < order.index("d")
    assert order.index("a") < order.index("c") < order.index("d")

def test_cycle_detected():
    g = DAG()
    g.add_edge("a","b"); g.add_edge("b","a")
    with pytest.raises(CycleError):
        g.topo()
    assert g.has_cycle()

def test_no_cycle():
    g = DAG()
    g.add_edge("a","b")
    assert not g.has_cycle()
