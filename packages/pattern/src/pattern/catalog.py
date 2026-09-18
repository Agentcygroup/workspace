from dataclasses import dataclass

PATTERNS = [
    {"name":"singleton","category":"creational","intent":"one instance"},
    {"name":"factory","category":"creational","intent":"defer construction"},
    {"name":"builder","category":"creational","intent":"stepwise construction"},
    {"name":"prototype","category":"creational","intent":"clone from exemplar"},
    {"name":"adapter","category":"structural","intent":"reconcile interfaces"},
    {"name":"bridge","category":"structural","intent":"separate abstraction from impl"},
    {"name":"composite","category":"structural","intent":"tree of parts"},
    {"name":"decorator","category":"structural","intent":"add behavior dynamically"},
    {"name":"facade","category":"structural","intent":"simplify subsystem"},
    {"name":"proxy","category":"structural","intent":"surrogate for another object"},
    {"name":"chain_of_responsibility","category":"behavioral","intent":"pass along until handled"},
    {"name":"command","category":"behavioral","intent":"reify request"},
    {"name":"interpreter","category":"behavioral","intent":"grammar as objects"},
    {"name":"iterator","category":"behavioral","intent":"sequential access"},
    {"name":"mediator","category":"behavioral","intent":"centralize interaction"},
    {"name":"memento","category":"behavioral","intent":"capture and restore state"},
    {"name":"observer","category":"behavioral","intent":"publish subscribe"},
    {"name":"state","category":"behavioral","intent":"behavior depends on state"},
    {"name":"strategy","category":"behavioral","intent":"interchangeable algorithms"},
    {"name":"template_method","category":"behavioral","intent":"skeleton with hooks"},
    {"name":"visitor","category":"behavioral","intent":"operations over structure"},
    {"name":"circuit_breaker","category":"resilience","intent":"stop calling failing service"},
    {"name":"bulkhead","category":"resilience","intent":"isolate failure domains"},
    {"name":"saga","category":"distributed","intent":"long-running transaction"},
    {"name":"cqrs","category":"distributed","intent":"separate read and write"},
    {"name":"event_sourcing","category":"distributed","intent":"state as event sequence"},
]

@dataclass
class Pattern:
    name: str
    category: str
    intent: str

def by_category(cat):
    return [p for p in PATTERNS if p["category"] == cat]

def is_pattern(name):
    return any(p["name"] == name for p in PATTERNS)
