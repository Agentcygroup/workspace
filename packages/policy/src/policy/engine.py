from dataclasses import dataclass, field

ALLOW = "allow"
DENY = "deny"

@dataclass
class Rule:
    name: str
    effect: str
    condition: callable
    priority: int = 0

@dataclass
class Decision:
    effect: str
    rule_name: str
    reason: str = ""

class Policy:
    def __init__(self, name="policy", default=DENY):
        self.name = name
        self.default = default
        self.rules = []

    def add(self, rule):
        if rule.effect not in (ALLOW, DENY):
            raise ValueError("bad effect: " + rule.effect)
        self.rules.append(rule)
        self.rules.sort(key=lambda r: -r.priority)
        return rule

    def evaluate(self, ctx):
        for r in self.rules:
            try:
                ok = r.condition(ctx)
            except Exception as e:
                return Decision(DENY, r.name, "condition error: " + str(e))
            if ok:
                return Decision(r.effect, r.name, "matched")
        return Decision(self.default, "<default>", "no rule matched")
