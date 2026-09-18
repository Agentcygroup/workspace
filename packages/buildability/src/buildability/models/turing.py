"""Turing machine."""
from __future__ import annotations
from ..model import Spec


def solver(spec: Spec) -> dict:
    return {
        "states": ["q0", "q_acc", "q_rej"],
        "transitions": [
            ("q0", "0", "q_acc", "0", "R"),
            ("q0", "1", "q_rej", "1", "R"),
        ],
        "spec": spec.name,
    }


def prover(candidate, spec: Spec) -> bool:
    if not isinstance(candidate, dict):
        return False
    trans = candidate.get("transitions")
    if not isinstance(trans, list) or not trans:
        return False
    for t in trans:
        if len(t) != 5 or t[4] not in ("L", "R"):
            return False
    return True


def resolver(a, b):
    if a == b:
        return 0
    na = len(a.get("transitions", []))
    nb = len(b.get("transitions", []))
    if na == nb:
        return None
    return -1 if na < nb else 1
