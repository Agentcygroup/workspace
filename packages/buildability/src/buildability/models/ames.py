"""AMES/AIMS substrate model."""
from __future__ import annotations


def solver(spec):
    return {"model": "ames", "substrate": spec.substrate}


def prover(candidate, spec):
    return isinstance(candidate, dict) and candidate.get("model") == "ames"


def resolver(a, b):
    if a is b:
        return 0
    if a == b:
        return 0
    return None
