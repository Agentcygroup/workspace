from core import sha256_hex, canonical_json

def test_sha256_stable():
    assert sha256_hex(b"hello") == sha256_hex(b"hello")
    assert sha256_hex(b"hello") != sha256_hex(b"world")

def test_canonical_json_sorted():
    a = canonical_json({"b": 2, "a": 1})
    b = canonical_json({"a": 1, "b": 2})
    assert a == b
