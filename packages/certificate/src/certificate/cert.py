from dataclasses import dataclass, field
import datetime

SIGNERS = ["H5_certifying_officer"]

@dataclass
class Certificate:
    certificate_id: str
    scope: str
    conformance_ids: list
    certified_by: str = ""
    certifier_role: str = "H5_certifying_officer"
    jurisdiction: dict = field(default_factory=dict)
    signed_utc: str = ""
    signature: str = ""
    expires_utc: str = ""
    revocation_url: str = ""

    def sign(self, signer, signature):
        if self.certifier_role not in SIGNERS:
            raise ValueError("role not authorized")
        if not signer:
            raise ValueError("signer required")
        if not self.conformance_ids:
            raise ValueError("at least one conformance id required")
        self.certified_by = signer
        self.signature = signature
        self.signed_utc = datetime.datetime.now(datetime.UTC).isoformat()
        return self

    def is_signed(self):
        return bool(self.signature) and bool(self.certified_by)
