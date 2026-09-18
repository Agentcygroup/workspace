from coverage import CoverageReport, Gap

def test_empty_report():
    c = CoverageReport("PU-1","snap.v1")
    assert c.ratio(0) == 0.0
    assert c.scoped_completion()

def test_ratio():
    c = CoverageReport("PU-1","snap.v1", touched=["a","b"])
    assert c.ratio(4) == 0.5

def test_gap_blocks_scoped():
    c = CoverageReport("PU-1","snap.v1", touched=["a"], gaps=[Gap("G-1","missing_source","x")])
    assert not c.scoped_completion()

def test_to_dict():
    c = CoverageReport("PU-1","snap.v1", touched=["a"])
    d = c.to_dict()
    assert d["unscoped_completion"] == "undefined"

def test_unscoped_always_undefined():
    c = CoverageReport("PU-1","snap.v1")
    assert c.to_dict()["unscoped_completion"] == "undefined"
