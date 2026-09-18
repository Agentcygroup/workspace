import hashlib
from dataclasses import dataclass, field
from pathlib import Path

def hash_bytes(b): return hashlib.sha256(b).hexdigest()
def hash_file(p):
    h = hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda: f.read(8192), b""): h.update(c)
    return h.hexdigest()

@dataclass
class EvidenceRef:
    evidence_id: str
    pointer: str
    strength: str
    hash_sha256: str = ""
    captured_utc: str = ""

@dataclass
class Provenance:
    steps: list = field(default_factory=list)

    def add(self, actor, action, target, hash_before="", hash_after=""):
        self.steps.append({"actor": actor, "action": action, "target": target,
                          "hash_before": hash_before, "hash_after": hash_after})
        return self.steps[-1]

    def validate(self):
        errs = []
        for i, s in enumerate(self.steps):
            for k in ["actor","action","target"]:
                if not s.get(k): errs.append(f"step {i}: missing {k}")
        return errs
