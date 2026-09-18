from dataclasses import dataclass, field
import datetime

class Verdict:
    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"
    NA = "not_applicable"
    ALL = [PASS, PARTIAL, FAIL, NA]

@dataclass
class ConformanceRecord:
    conformance_id: str
    claim_id: str
    citation_id: str
    clause: str
    criterion: str
    evidence_refs: list = field(default_factory=list)
    assessed_by: str = ""
    assessed_utc: str = ""
    verdict: str = ""

    def assess(self, assessor, verdict):
        if verdict not in Verdict.ALL:
            raise ValueError("bad verdict")
        if not assessor:
            raise ValueError("assessor required")
        if not self.evidence_refs:
            raise ValueError("at least one evidence ref required")
        self.assessed_by = assessor
        self.verdict = verdict
        self.assessed_utc = datetime.datetime.now(datetime.UTC).isoformat()
        return self
