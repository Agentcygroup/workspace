from dataclasses import dataclass, field

@dataclass
class Jurisdiction:
    code: str
    name: str = ""
    residency_required: bool = True

@dataclass
class Boundary:
    jurisdiction: Jurisdiction
    allowed_egress: list = field(default_factory=list)
    blocked_egress: list = field(default_factory=list)

    def permits(self, target):
        if target in self.blocked_egress:
            return False
        if self.allowed_egress and target not in self.allowed_egress:
            return False
        return True

@dataclass
class RouteDecision:
    allow: bool
    reason: str

@dataclass
class Route:
    source: Boundary
    target: Boundary

    def evaluate(self, payload_kind="data"):
        if not self.source.permits(self.target.jurisdiction.code):
            return RouteDecision(False, "source forbids egress to " + self.target.jurisdiction.code)
        if self.target.jurisdiction.residency_required and payload_kind == "personal":
            return RouteDecision(False, "residency required at target")
        return RouteDecision(True, "route permitted")
