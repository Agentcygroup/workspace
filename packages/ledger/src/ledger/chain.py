import hashlib, json
from pathlib import Path

class ChainError(Exception):
    pass

def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()

def _sha(b):
    return hashlib.sha256(b).hexdigest()

class Chain:
    def __init__(self, entries=None):
        self.entries = entries or []
        self._verify()

    def _verify(self):
        prev = "0" * 64
        for i, e in enumerate(self.entries):
            if e.get("prev") != prev:
                raise ChainError(f"entry {i}: prev mismatch")
            body = {k: v for k, v in e.items() if k != "hash"}
            if _sha(_canon(body)) != e.get("hash"):
                raise ChainError(f"entry {i}: hash mismatch")
            prev = e["hash"]

    def append(self, payload):
        prev = self.entries[-1]["hash"] if self.entries else "0" * 64
        body = {"index": len(self.entries), "prev": prev, "payload": payload}
        entry = dict(body); entry["hash"] = _sha(_canon(body))
        self.entries.append(entry)
        return entry

    def head(self):
        return self.entries[-1]["hash"] if self.entries else "0" * 64

    def to_dict(self):
        return {"entries": self.entries, "head": self.head(), "length": len(self.entries)}

    @classmethod
    def from_dict(cls, d):
        return cls(entries=d.get("entries", []))

    def save(self, path):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path):
        return cls.from_dict(json.loads(Path(path).read_text()))
