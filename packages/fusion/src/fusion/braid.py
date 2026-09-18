import hashlib, json
from dataclasses import dataclass, field

class Modality:
    TEXT = "text"
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    ALL = [TEXT, NUMERIC, CATEGORICAL]

def _hash(o): return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

@dataclass
class Braid:
    modalities: dict = field(default_factory=dict)
    weights: dict = field(default_factory=dict)
    def add(self, name, modality, value, weight=1.0):
        if modality not in Modality.ALL:
            raise ValueError("unknown modality: " + modality)
        if not isinstance(weight, (int, float)) or weight < 0:
            raise ValueError("weight must be non-negative")
        self.modalities[name] = {"modality": modality, "value": value, "weight": weight}
        return self.modalities[name]
    def fuse(self):
        text = []
        numeric = []
        categorical = []
        for name, m in self.modalities.items():
            if m["modality"] == Modality.TEXT:
                text.append(str(m["value"]))
            elif m["modality"] == Modality.NUMERIC:
                numeric.append(float(m["value"]) * m["weight"])
            elif m["modality"] == Modality.CATEGORICAL:
                categorical.append(str(m["value"]))
        n = sum(numeric) / len(numeric) if numeric else 0.0
        return {
            "text": " | ".join(text),
            "numeric_mean": n,
            "categorical": sorted(set(categorical)),
            "hash": _hash([text, numeric, categorical]),
        }

def fuse(signals):
    b = Braid()
    for s in signals:
        b.add(s["name"], s["modality"], s["value"], s.get("weight", 1.0))
    return b.fuse()
