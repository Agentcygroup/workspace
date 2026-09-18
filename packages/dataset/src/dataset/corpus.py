import hashlib, json
from dataclasses import dataclass, field

def _fp(text): return hashlib.sha256(text.encode()).hexdigest()

@dataclass
class Record:
    id: str
    content: str
    source: str = ""
    lineage: list = field(default_factory=list)

@dataclass
class Lineage:
    steps: list = field(default_factory=list)
    def add(self, op, detail=""):
        self.steps.append({"op": op, "detail": detail})
        return self.steps[-1]

@dataclass
class Corpus:
    records: dict = field(default_factory=dict)
    dropped: list = field(default_factory=list)
    def add(self, content, source="", lineage=None):
        fp = _fp(content)
        if fp in self.records:
            self.dropped.append({"reason": "duplicate", "fingerprint": fp})
            return None
        rec = Record(id=fp[:16], content=content, source=source, lineage=(lineage.steps if lineage else []))
        self.records[fp] = rec
        return rec
    def size(self): return len(self.records)
    def fingerprints(self): return sorted(self.records.keys())
    def to_dict(self):
        return {"size": self.size(), "dropped": len(self.dropped),
                "records": [{"id": r.id, "source": r.source, "lineage": r.lineage} for r in self.records.values()]}
