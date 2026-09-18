from dataclasses import dataclass, field
import datetime

@dataclass
class Citation:
    citation_id: str
    source_authority: str
    source_publication: str
    clause: str
    quote: str
    locator: str
    verified_by: str = ""
    verified_utc: str = ""
    confidence: float = 0.0

    def verify(self, verifier, confidence):
        if not 0 <= confidence <= 1:
            raise ValueError("confidence out of range")
        if not verifier:
            raise ValueError("verifier required")
        self.verified_by = verifier
        self.confidence = confidence
        self.verified_utc = datetime.datetime.now(datetime.UTC).isoformat()
        return self

    def is_verified(self):
        return bool(self.verified_by)
