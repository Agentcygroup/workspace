from dataclasses import dataclass, field

@dataclass
class Publication:
    ref: str
    covers: list = field(default_factory=list)

@dataclass
class Source:
    source_id: str
    name: str
    type: str
    scope: list = field(default_factory=list)
    publications: list = field(default_factory=list)

    def add_publication(self, ref, covers=None):
        self.publications.append(Publication(ref, covers or []))
        return self.publications[-1]

    def to_dict(self):
        return {"source_id": self.source_id, "name": self.name, "type": self.type,
                "scope": list(self.scope),
                "publications": [{"ref": p.ref, "covers": list(p.covers)} for p in self.publications]}
