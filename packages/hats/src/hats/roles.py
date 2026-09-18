from dataclasses import dataclass, field

HATS = [
    "developer","architect","sre","security_engineer","dba","pm","tech_lead",
    "data_engineer","ml_engineer","qa","devops","platform","researcher",
    "founder","cto","reviewer","auditor","compliance_officer","privacy_officer",
    "incident_commander","on_call","network_engineer","hardware_engineer",
    "systems_engineer","firmware_engineer","research_scientist","analyst",
    "designer","writer","community_manager","release_manager","program_manager",
    "risk_officer","legal_counsel","support_engineer","sales_engineer",
]

@dataclass
class Hat:
    name: str
    capabilities: list = field(default_factory=list)
    boundaries: list = field(default_factory=list)
    def can(self, action): return action in self.capabilities
    def may_not(self, action): return action in self.boundaries

def hats_by_discipline():
    return {
        "engineering": [h for h in HATS if h in ("developer","architect","tech_lead","systems_engineer","platform","devops","sre")],
        "security": [h for h in HATS if h in ("security_engineer","auditor","incident_commander","risk_officer")],
        "data": [h for h in HATS if h in ("data_engineer","dba","analyst","research_scientist","ml_engineer")],
        "product": [h for h in HATS if h in ("pm","program_manager","designer","writer")],
        "governance": [h for h in HATS if h in ("compliance_officer","privacy_officer","legal_counsel","auditor")],
    }

def is_hat(name): return name in HATS
