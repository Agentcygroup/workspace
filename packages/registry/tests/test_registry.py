from registry import Registry, Source, Publication

def test_source_add_publication():
    s = Source("SRC-ISO","ISO","treaty")
    s.add_publication("ISO-27001",["isms"])
    assert len(s.publications) == 1

def test_registry_add_and_count():
    r = Registry()
    s = Source("SRC-ISO","ISO","treaty")
    s.add_publication("ISO-27001")
    s.add_publication("ISO-25010")
    r.add_source(s)
    assert r.entry_count() == 2

def test_freeze_snapshot_stable():
    r = Registry()
    r.add_source(Source("A","a","t").__class__("A","a","t") if False else Source("A","a","t"))
    s1 = r.freeze()
    s2 = r.freeze()
    assert s1["hash"] == s2["hash"]

def test_snapshot_lists_sources():
    r = Registry()
    r.add_source(Source("A","a","t"))
    r.add_source(Source("B","b","t"))
    snap = r.freeze("v0")
    assert snap["sources"] == ["A","B"]
