from dataclasses import dataclass, field

HANDS = [
    "code","test","review","design","debug","deploy","operate","monitor",
    "estimate","document","mentor","model","simulate","analyze","profile",
    "optimize","refactor","migrate","integrate","automate","secure","audit",
    "certify","govern","plan","schedule","budget","hire","train","research",
    "publish","maintain","retire","recover","respond","detect","harden",
]

FAMILIES = {
    "build": ["code","test","review","design","refactor","integrate"],
    "operate": ["deploy","operate","monitor","maintain","recover","respond"],
    "protect": ["secure","audit","harden","certify","detect"],
    "reason": ["analyze","model","simulate","profile","estimate"],
    "organize": ["plan","schedule","budget","govern"],
    "grow": ["mentor","train","research","publish"],
}

@dataclass
class Hand:
    name: str
    family: str = ""
    proficiency: str = "novice"
    def upgrade(self, level):
        if level not in ("novice","competent","proficient","expert"):
            raise ValueError("bad proficiency")
        self.proficiency = level
        return self

def hands_by_family():
    return {k: list(v) for k, v in FAMILIES.items()}

def is_hand(name): return name in HANDS
