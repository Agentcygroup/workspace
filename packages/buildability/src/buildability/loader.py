"""Load a Spec from the on-disk JSON shape. Single source of truth."""
from __future__ import annotations
import json
from pathlib import Path
from .model import Spec, Component, Interface, Invariant, Lifecycle, Gap


def spec_from_dict(raw: dict, *, name: str | None = None) -> Spec:
    return Spec(
        name=name or raw.get("kind_id", "unnamed"),
        components=tuple(Component(**c) for c in raw.get("components", [])),
        interfaces=tuple(Interface(**i) for i in raw.get("interfaces", [])),
        invariants=tuple(Invariant(**v) for v in raw.get("invariants", [])),
        lifecycle=Lifecycle(**raw["lifecycle"]) if raw.get("lifecycle") else None,
        substrate=raw.get("substrate") or raw.get("level"),
        substrate_available=bool(raw.get("substrate") or raw.get("level")),
        model=raw.get("model"),
        gaps=tuple(Gap(**g) for g in raw.get("gaps", [])),
    )


def spec_from_file(p: Path | str) -> Spec:
    p = Path(p)
    return spec_from_dict(json.loads(p.read_text()), name=p.stem)


import hashlib as _hashlib


def spec_identity(spec):
    """SHA-256 over the spec's canonical content."""
    import json as _json
    payload = {
        "name": spec.name,
        "components": sorted((c.name, c.responsibility) for c in spec.components),
        "interfaces": sorted((i.name, i.schema, i.protocol, i.version) for i in spec.interfaces),
        "invariants": sorted((v.name, v.predicate) for v in spec.invariants),
        "substrate": spec.substrate,
    }
    blob = _json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return _hashlib.sha256(blob.encode()).hexdigest()
