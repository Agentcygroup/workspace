import json, datetime
from pathlib import Path
from ledger import Chain, ChainError

def _now(): return datetime.datetime.now(datetime.UTC).isoformat()

class AuditEvent:
    def __init__(self, actor, action, target, result, non_implication=""):
        self.actor = actor
        self.action = action
        self.target = target
        self.result = result
        self.non_implication = non_implication
        self.ts = _now()
    def to_dict(self):
        return {"ts": self.ts, "actor": self.actor, "action": self.action,
                "target": self.target, "result": self.result,
                "non_implication": self.non_implication}

class AuditLog:
    def __init__(self, chain=None):
        self.chain = chain or Chain()

    def append(self, event):
        if isinstance(event, AuditEvent):
            event = event.to_dict()
        return self.chain.append(event)

    def count(self):
        return len(self.chain.entries)

    def verify(self):
        Chain(self.chain.entries)
        return True

    def save(self, path): self.chain.save(path)

    @classmethod
    def load(cls, path): return cls(Chain.load(path))
