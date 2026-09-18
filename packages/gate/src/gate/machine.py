GATES = ["H1_registry_curator","H2_coverage_reviewer","H3_citation_verifier","H4_conformance_assessor","H5_certifying_officer","H6_jurisdiction_checker"]

TRANSITIONS = [
    ("draft","H1_signed","H1_registry_curator"),
    ("H1_signed","H2_signed","H2_coverage_reviewer"),
    ("H2_signed","H3_signed","H3_citation_verifier"),
    ("H3_signed","H4_signed","H4_conformance_assessor"),
    ("H4_signed","H5_signed","H5_certifying_officer"),
    ("H5_signed","H6_checked","H6_jurisdiction_checker"),
    ("H6_checked","certified","H5_certifying_officer"),
]

class GateError(Exception):
    pass

class GateMachine:
    def __init__(self):
        self.state = "draft"
        self.history = [{"state": "draft", "by": None}]

    def sign(self, gate, signer):
        if gate not in GATES:
            raise GateError("unknown gate: " + gate)
        for src, dst, g in TRANSITIONS:
            if src == self.state and g == gate:
                self.state = dst
                self.history.append({"state": dst, "by": signer, "gate": gate})
                return dst
        raise GateError(f"gate {gate} not allowed from state {self.state}")

    def revoke(self, signer):
        self.state = "revoked"
        self.history.append({"state": "revoked", "by": signer})

    def is_certified(self):
        return self.state == "certified"
