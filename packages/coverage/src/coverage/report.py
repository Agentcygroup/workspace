from dataclasses import dataclass, field

@dataclass
class Gap:
    gap_id: str
    gap_type: str
    target: str
    status: str = "open"

@dataclass
class CoverageReport:
    pu_id: str
    registry_snapshot: str
    touched: list = field(default_factory=list)
    untouchable: list = field(default_factory=list)
    gaps: list = field(default_factory=list)

    def ratio(self, universe_size):
        if universe_size <= 0:
            return 0.0
        return len(self.touched) / universe_size

    def scoped_completion(self):
        return len(self.gaps) == 0

    def to_dict(self):
        return {
            "pu_id": self.pu_id,
            "registry_snapshot": self.registry_snapshot,
            "touched": list(self.touched),
            "untouchable": list(self.untouchable),
            "gaps": [{"gap_id": g.gap_id, "gap_type": g.gap_type, "target": g.target, "status": g.status} for g in self.gaps],
            "scoped_completion": self.scoped_completion(),
            "unscoped_completion": "undefined",
        }
