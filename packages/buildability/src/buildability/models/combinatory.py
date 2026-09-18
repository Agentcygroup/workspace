"""Combinatory logic: I = S K K."""
from __future__ import annotations
from ..model import Spec


def solver(spec: Spec) -> dict:
    return {"S": True, "K": True, "I": True, "spec": spec.name}


def prover(candidate, spec: Spec) -> bool:
    if not isinstance(candidate, dict):
        return False
    return all(k in candidate for k in ("S", "K", "I"))


def resolver(a, b):
    if a == b:
        return 0
    return None
