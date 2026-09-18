from dataset import Corpus, Lineage

def test_add_record():
    c = Corpus()
    r = c.add("hello")
    assert r is not None
    assert c.size() == 1

def test_deduplicate():
    c = Corpus()
    c.add("hello")
    c.add("hello")
    assert c.size() == 1
    assert len(c.dropped) == 1

def test_fingerprint_stable():
    c1 = Corpus(); c2 = Corpus()
    c1.add("x"); c2.add("x")
    assert c1.fingerprints() == c2.fingerprints()

def test_lineage():
    l = Lineage()
    l.add("fetch", "url")
    l.add("clean", "strip")
    c = Corpus()
    r = c.add("y", source="s", lineage=l)
    assert len(r.lineage) == 2

def test_to_dict():
    c = Corpus()
    c.add("a")
    d = c.to_dict()
    assert d["size"] == 1
