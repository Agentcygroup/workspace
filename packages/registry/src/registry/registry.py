import hashlib, json
from .sources import Source

def _canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()
def _sha(b): return hashlib.sha256(b).hexdigest()

class Registry:
    def __init__(self, version="0.1.0"):
        self.version = version
        self.sources = {}
        self.snapshots = {}

    def add_source(self, src):
        self.sources[src.source_id] = src
        return src

    def freeze(self, snap_id=None):
        snap_id = snap_id or f"v{self.version}"
        payload = self.to_dict()
        h = _sha(_canon(payload))
        self.snapshots[snap_id] = {"id": snap_id, "hash": h, "sources": sorted(self.sources.keys())}
        return self.snapshots[snap_id]

    def to_dict(self):
        return {"version": self.version, "sources": [s.to_dict() for s in self.sources.values()]}

    def entry_count(self):
        return sum(len(s.publications) for s in self.sources.values())
