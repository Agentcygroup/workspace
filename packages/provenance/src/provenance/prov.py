from dataclasses import dataclass, field
import datetime

@dataclass
class Agent:
    id: str
    kind: str = "human"

@dataclass
class Entity:
    id: str
    hash_sha256: str = ""

@dataclass
class Activity:
    id: str
    agent: Agent = None
    used: list = field(default_factory=list)
    generated: list = field(default_factory=list)
    ts: str = ""
    def __post_init__(self):
        if not self.ts:
            self.ts = datetime.datetime.now(datetime.UTC).isoformat()

@dataclass
class Chain:
    activities: list = field(default_factory=list)
    entities: dict = field(default_factory=dict)
    agents: dict = field(default_factory=dict)

    def add_entity(self, e):
        self.entities[e.id] = e
        return e

    def add_agent(self, a):
        self.agents[a.id] = a
        return a

    def add_activity(self, a):
        for u in a.used:
            if u not in self.entities:
                raise ValueError("unknown used entity: " + u)
        for g in a.generated:
            if g not in self.entities:
                raise ValueError("unknown generated entity: " + g)
        if a.agent and a.agent.id not in self.agents:
            raise ValueError("unknown agent: " + a.agent.id)
        self.activities.append(a)
        return a

    def to_dict(self):
        return {
            "activities": [{"id": a.id, "agent": a.agent.id if a.agent else None, "used": a.used, "generated": a.generated, "ts": a.ts} for a in self.activities],
            "entities": [{"id": e.id, "hash": e.hash_sha256} for e in self.entities.values()],
            "agents": [{"id": g.id, "kind": g.kind} for g in self.agents.values()],
        }
