import hashlib, json, datetime
from dataclasses import dataclass, field
from pathlib import Path

def _sha(b): return hashlib.sha256(b).hexdigest()

def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(8192), b""): h.update(c)
    return h.hexdigest()

def canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()

@dataclass
class Subject:
    name: str
    digest: str
    size: int = 0

@dataclass
class Statement:
    type_: str
    subjects: list = field(default_factory=list)
    predicate: dict = field(default_factory=dict)
    created_utc: str = ""
    def __post_init__(self):
        if not self.created_utc:
            self.created_utc = datetime.datetime.now(datetime.UTC).isoformat()
    def to_dict(self):
        return {"_type": self.type_,
                "subject": [{"name": s.name, "digest": {"sha256": s.digest}, "size": s.size} for s in self.subjects],
                "predicate": self.predicate,
                "created_utc": self.created_utc}
    def hash(self):
        return _sha(canon(self.to_dict()))

def build_statement(name, predicate, paths):
    subs = []
    for p in paths:
        p = Path(p)
        if not p.exists(): continue
        subs.append(Subject(p.name, sha_file(p), p.stat().st_size))
    return Statement(type_="https://in-toto.io/Statement/v1", subjects=subs, predicate=predicate)
