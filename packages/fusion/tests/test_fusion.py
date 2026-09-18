import pytest
from fusion import Braid, Modality, fuse

def test_add_and_fuse():
    b = Braid()
    b.add("caption", Modality.TEXT, "hello")
    b.add("score", Modality.NUMERIC, 5, weight=2.0)
    b.add("label", Modality.CATEGORICAL, "cat")
    r = b.fuse()
    assert r["text"] == "hello"
    assert r["numeric_mean"] == 10.0
    assert r["categorical"] == ["cat"]

def test_bad_modality():
    b = Braid()
    with pytest.raises(ValueError):
        b.add("x", "smell", 1)

def test_bad_weight():
    b = Braid()
    with pytest.raises(ValueError):
        b.add("x", Modality.TEXT, "a", weight=-1)

def test_fuse_convenience():
    r = fuse([{"name":"t","modality":Modality.TEXT,"value":"x"}])
    assert r["text"] == "x"

def test_hash_stable():
    r1 = fuse([{"name":"t","modality":Modality.TEXT,"value":"x"}])
    r2 = fuse([{"name":"t","modality":Modality.TEXT,"value":"x"}])
    assert r1["hash"] == r2["hash"]
