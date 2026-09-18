from pmap import PMap

def test_empty():
    m = PMap()
    assert m.size() == 0

def test_set_returns_new():
    a = PMap()
    b = a.set("x", 1)
    assert a.size() == 0
    assert b.size() == 1

def test_get():
    m = PMap().set("x", 1)
    assert m.get("x") == 1
    assert m.get("y") is None
    assert m.get("y", "default") == "default"

def test_remove():
    m = PMap().set("x", 1).set("y", 2)
    r = m.remove("x")
    assert not r.contains("x")
    assert m.contains("x")

def test_keys_and_size():
    m = PMap().set("a", 1).set("b", 2)
    assert set(m.keys()) == {"a","b"}
    assert m.size() == 2

def test_merge():
    a = PMap().set("x", 1)
    b = PMap().set("y", 2)
    c = a.merge(b)
    assert c.size() == 2
    assert c.get("x") == 1 and c.get("y") == 2
