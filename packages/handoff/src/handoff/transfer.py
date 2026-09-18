from dataclasses import dataclass, field
import datetime

class Mode:
    ASSIGNMENT = "assignment"
    DELEGATION = "delegation"
    REFERRAL = "referral"
    ESCALATION = "escalation"
    REVIEW = "review_request"
    ALL = [ASSIGNMENT, DELEGATION, REFERRAL, ESCALATION, REVIEW]

class HandoffState:
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    RETURNED = "returned"
    ESCALATED = "escalated"

@dataclass
class Handoff:
    sender: str
    receiver: str
    mode: str
    object_id: str
    authority_attached: list = field(default_factory=list)
    authority_not_attached: list = field(default_factory=list)
    acceptance_criteria: str = ""
    state: str = HandoffState.PROPOSED
    ts: str = ""
    def __post_init__(self):
        if self.mode not in Mode.ALL:
            raise ValueError("unknown mode: " + self.mode)
        if not self.ts:
            self.ts = datetime.datetime.now(datetime.UTC).isoformat()

    def accept(self):
        if self.state != HandoffState.PROPOSED:
            raise ValueError("cannot accept from state " + self.state)
        self.state = HandoffState.ACCEPTED
        return self

    def reject(self):
        if self.state != HandoffState.PROPOSED:
            raise ValueError("cannot reject from state " + self.state)
        self.state = HandoffState.REJECTED
        return self
