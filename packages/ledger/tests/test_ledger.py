import pytest
from ledger import Chain, ChainError, Claim, Evidence, Link, validate_link
from pathlib import Path

def test_chain_starts_empty():
    c = Chain()
    assert c.head() == "0"*64
    assert len(c.entries) == 0

def test_chain_append_and_verify():
    c = Chain()
    c.append({"x": 1})
    c.append({"y": 2})
    assert len(c.entries) == 2
    Chain(c.entries)  # re-verify

def test_chain_tamper_detected():
    c = Chain()
    c.append({"x": 1})
    c.entries[0]["payload"]["x"] = 999
    with pytest.raises(ChainError):
        Chain(c.entries)

def test_chain_save_load(tmp_path):
    c = Chain()
    c.append({"a": 1})
    p = tmp_path / "chain.json"
    c.save(p)
    c2 = Chain.load(p)
    assert c2.head() == c.head()

def test_claim_validate():
    c = Claim("C-001","x","security","high",["E-001"])
    assert c.validate() == []

def test_claim_bad_id():
    c = Claim("X","x","security","high")
    assert c.validate()

def test_evidence_validate():
    e = Evidence("E-001","test_result","path","strong")
    assert e.validate() == []

def test_link_validate():
    l = Link("C-001","E-001","supports")
    assert l.validate() == []
    assert validate_link(l, {"C-001"}, {"E-001"}) == []

def test_link_unknown_refs():
    l = Link("C-001","E-001","supports")
    errs = validate_link(l, set(), set())
    assert len(errs) == 2
