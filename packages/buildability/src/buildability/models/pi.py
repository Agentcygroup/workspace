"""Pi calculus."""
from __future__ import annotations
from ..model import Spec


def solver(spec: Spec) -> dict:
    return {"process": "0", "channels": [i.name for i in spec.interfaces]}


def prover(candidate, spec: Spec) -> bool:
    if not isinstance(candidate, dict):
        return False
    return "process" in candidate and "channels" in candidate


def resolver(a, b):
    if a == b:
        return 0
    ca = len(a.get("channels", []))
    cb = len(b.get("channels", []))
    if ca == cb:
        return None
    return -1 if ca < cb else 1
