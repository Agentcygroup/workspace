import uuid, datetime
from dataclasses import dataclass, field

class DisputeState:
    FILED = "filed"
    UNDER_REVIEW = "under_review"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    WITHDRAWN = "withdrawn"
    STATES = [FILED, UNDER_REVIEW, ESCALATED, RESOLVED, WITHDRAWN]

class Transition:
    @staticmethod
    def allowed(state):
        return {
            DisputeState.FILED: [DisputeState.UNDER_REVIEW, DisputeState.WITHDRAWN],
            DisputeState.UNDER_REVIEW: [DisputeState.ESCALATED, DisputeState.RESOLVED],
            DisputeState.ESCALATED: [DisputeState.RESOLVED, DisputeState.WITHDRAWN],
            DisputeState.RESOLVED: [],
            DisputeState.WITHDRAWN: [],
        }.get(state, [])

@dataclass
class File:
    filer: str
    respondent: str
    claim: str
    evidence_refs: list = field(default_factory=list)

@dataclass
class Dispute:
    case_id: str = ""
    file: File = None
    state: str = DisputeState.FILED
    history: list = field(default_factory=list)
    def __post_init__(self):
        if not self.case_id:
            self.case_id = "DSP-" + uuid.uuid4().hex[:12]
        self.history.append({"state": self.state, "ts": datetime.datetime.now(datetime.UTC).isoformat()})

    def transition(self, to_state, by):
        if to_state not in DisputeState.STATES:
            raise ValueError("unknown state: " + to_state)
        if to_state not in Transition.allowed(self.state):
            raise ValueError("illegal transition: " + self.state + " -> " + to_state)
        self.state = to_state
        self.history.append({"state": to_state, "by": by, "ts": datetime.datetime.now(datetime.UTC).isoformat()})
        return to_state
