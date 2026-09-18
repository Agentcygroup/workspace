import pytest
from protocol import Protocol, Message, ProtocolError

def test_register_and_encode():
    p = Protocol("test")
    p.register("ping")
    framed = p.encode(Message("ping", {"x":1}))
    assert "body" in framed and "hash" in framed

def test_unregistered_kind():
    p = Protocol("test")
    with pytest.raises(ProtocolError):
        p.encode(Message("unknown"))

def test_roundtrip():
    p = Protocol("test")
    p.register("ping")
    m = Message("ping", {"x":1}, 42)
    d = p.decode(p.encode(m))
    assert d.kind == "ping" and d.nonce == 42

def test_tamper_detected():
    p = Protocol("test")
    p.register("ping")
    framed = p.encode(Message("ping"))
    framed["body"] = framed["body"].replace("ping","pong")
    with pytest.raises(ProtocolError):
        p.decode(framed)

def test_version_mismatch():
    p1 = Protocol("test", "1.0.0"); p1.register("ping")
    p2 = Protocol("test", "2.0.0"); p2.register("ping")
    framed = p1.encode(Message("ping"))
    with pytest.raises(ProtocolError):
        p2.decode(framed)
