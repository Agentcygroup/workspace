import re
from dataclasses import dataclass, field

CLAIM_RE = re.compile(r"^C-\d{3,5}$")
EVD_RE = re.compile(r"^E-\d{3,5}$")
LINK_TYPES = {"supports","contradicts","contextualizes","supersedes"}

@dataclass
class Claim:
    claim_id: str
    text: str
    type: str
    criticality: str
    evidence_refs: list = field(default_factory=list)

    def validate(self):
        errs = []
        if not CLAIM_RE.match(self.claim_id): errs.append("bad claim_id")
        if not self.text: errs.append("empty text")
        if self.criticality not in ("low","medium","high","critical"): errs.append("bad criticality")
        return errs

@dataclass
class Evidence:
    evidence_id: str
    type: str
    pointer: str
    strength: str
    hash_sha256: str = ""

    def validate(self):
        errs = []
        if not EVD_RE.match(self.evidence_id): errs.append("bad evidence_id")
        if not self.pointer: errs.append("empty pointer")
        if self.strength not in ("weak","moderate","strong","conclusive"): errs.append("bad strength")
        return errs

@dataclass
class Link:
    claim_id: str
    evidence_id: str
    link_type: str

    def validate(self):
        errs = []
        if not CLAIM_RE.match(self.claim_id): errs.append("bad claim_id")
        if not EVD_RE.match(self.evidence_id): errs.append("bad evidence_id")
        if self.link_type not in LINK_TYPES: errs.append("bad link_type")
        return errs

def validate_link(link, claim_ids, evidence_ids):
    errs = link.validate()
    if link.claim_id not in claim_ids: errs.append("unknown claim")
    if link.evidence_id not in evidence_ids: errs.append("unknown evidence")
    return errs
