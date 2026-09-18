from dataclasses import dataclass, field

LENSES = [
    "security","performance","cost","reliability","privacy","ethics",
    "accessibility","maintainability","scalability","observability","compliance",
    "business_value","threat","failure_mode","data_flow","usability",
    "sustainability","portability","interoperability","testability","modularity",
    "simplicity","consistency","correctness","safety","resilience","trust",
    "governance","sovereignty","equity",
]

@dataclass
class Lens:
    name: str
    questions: list = field(default_factory=list)
    def ask(self): return list(self.questions)

def lens_questions(name):
    table = {
        "security": ["what can an attacker do","what is the blast radius","what controls exist"],
        "performance": ["what is the latency","what is the throughput","where is the bottleneck"],
        "cost": ["what does it cost to run","where does the money go","can it be cheaper"],
        "reliability": ["what fails","how does it recover","what is the SLO"],
        "privacy": ["what personal data is processed","where does it go","what is the lawful basis"],
        "ethics": ["who is affected","what harms are possible","who decides"],
        "compliance": ["what clauses apply","which are met","which are gaps"],
        "governance": ["who owns this","what authority exists","how is it revoked"],
    }
    return table.get(name, ["what does this lens reveal"])

def is_lens(name): return name in LENSES
