import pytest
from conformance import ConformanceRecord, Verdict

def test_construct():
    c = ConformanceRecord("CF-1","C-001","CIT-1","2.1","criterion",["E-001"])
    assert c.verdict == ""

def test_assess_pass():
    c = ConformanceRecord("CF-1","C-001","CIT-1","2.1","crit",["E-001"])
    c.assess("human.bob", Verdict.PASS)
    assert c.verdict == Verdict.PASS

def test_assess_bad_verdict():
    c = ConformanceRecord("CF-1","C-001","CIT-1","2.1","c",["E-001"])
    with pytest.raises(ValueError):
        c.assess("a","nonsense")

def test_assess_requires_evidence():
    c = ConformanceRecord("CF-1","C-001","CIT-1","2.1","c",[])
    with pytest.raises(ValueError):
        c.assess("a", Verdict.PASS)

def test_assess_requires_name():
    c = ConformanceRecord("CF-1","C-001","CIT-1","2.1","c",["E-001"])
    with pytest.raises(ValueError):
        c.assess("", Verdict.PASS)
