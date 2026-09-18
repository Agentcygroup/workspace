"""Category theory: id, composition."""
from __future__ import annotations
from ..model import Spec


def solver(spec: Spec) -> dict:
    objects = [c.name for c in spec.components]
    arrows = [(i.name, o) for i in spec.interfaces for o in objects]
    return {"objects": objects, "arrows": arrows, "identity": True}


def prover(candidate, spec: Spec) -> bool:
    if not isinstance(candidate, dict):
        return False
    if "objects" not in candidate or "arrows" not in candidate:
        return False
    return candidate.get("identity") is True


def resolver(a, b):
    if a == b:
        return 0
    aa = len(a.get("arrows", []))
    ab = len(b.get("arrows", []))
    if aa == ab:
        return None
    return -1 if aa < ab else 1
