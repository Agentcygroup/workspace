"""Load a Spec from the on-disk JSON shape. Single source of truth."""
from __future__ import annotations
import json
from pathlib import Path
from .model import Spec, Component, Interface, Invariant, Lifecycle, Gap


def spec_from_dict(raw: dict, *, name: str | None = None) -> Spec:
    return Spec(
        name=name or raw.get("kind_id", "unnamed"),
        components=[Component(**c) for c in raw.get("components", [])],
        interfaces=[Interface(**i) for i in raw.get("interfaces", [])],
        invariants=[Invariant(**v) for v in raw.get("invariants", [])],
        lifecycle=Lifecycle(**raw["lifecycle"]) if raw.get("lifecycle") else None,
        substrate=raw.get("substrate") or raw.get("level"),
        substrate_available=bool(raw.get("substrate") or raw.get("level")),
        gaps=[Gap(**g) for g in raw.get("gaps", [])],
    )


def spec_from_file(p: Path | str) -> Spec:
    p = Path(p)
    return spec_from_dict(json.loads(p.read_text()), name=p.stem)
