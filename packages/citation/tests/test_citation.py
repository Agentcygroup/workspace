import pytest
from citation import Citation

def test_citation_construct():
    c = Citation("CIT-1","SRC-NIST","SP 800-207","2.1","quote","https://doi.org/...")
    assert not c.is_verified()

def test_verify_sets_fields():
    c = Citation("CIT-1","SRC-NIST","SP 800-207","2.1","q","loc")
    c.verify("human.alice", 0.9)
    assert c.is_verified()
    assert c.verified_by == "human.alice"

def test_verify_rejects_bad_confidence():
    c = Citation("CIT-1","X","Y","Z","q","l")
    with pytest.raises(ValueError):
        c.verify("a", 1.5)

def test_verify_requires_name():
    c = Citation("CIT-1","X","Y","Z","q","l")
    with pytest.raises(ValueError):
        c.verify("", 0.5)
