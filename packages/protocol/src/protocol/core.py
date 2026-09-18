import json, hashlib
from dataclasses import dataclass, field

class ProtocolError(Exception):
    pass

@dataclass
class Message:
    kind: str
    payload: dict = field(default_factory=dict)
    nonce: int = 0

class Protocol:
    def __init__(self, name, version="1.0.0"):
        self.name = name
        self.version = version
        self.kinds = set()

    def register(self, kind):
        self.kinds.add(kind)
        return kind

    def encode(self, msg):
        if msg.kind not in self.kinds:
            raise ProtocolError("unregistered kind: " + msg.kind)
        body = json.dumps({"kind": msg.kind, "payload": msg.payload, "nonce": msg.nonce, "version": self.version}, sort_keys=True).encode()
        return {"body": body.decode(), "hash": hashlib.sha256(body).hexdigest()}

    def decode(self, framed):
        body = framed["body"].encode()
        if hashlib.sha256(body).hexdigest() != framed.get("hash"):
            raise ProtocolError("hash mismatch")
        d = json.loads(body)
        if d.get("version") != self.version:
            raise ProtocolError("version mismatch")
        if d["kind"] not in self.kinds:
            raise ProtocolError("unregistered kind: " + d["kind"])
        return Message(d["kind"], d["payload"], d["nonce"])
