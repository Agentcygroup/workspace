"""Cellular automata, rule 110."""
from __future__ import annotations
from ..model import Spec


RULE_110 = {
    (1, 1, 1): 0, (1, 1, 0): 1, (1, 0, 1): 1, (1, 0, 0): 0,
    (0, 1, 1): 1, (0, 1, 0): 1, (0, 0, 1): 1, (0, 0, 0): 0,
}


def solver(spec: Spec) -> dict:
    n = max(1, len(spec.components))
    return {
        "rule": "110",
        "width": n,
        "initial": [0] * (n // 2) + [1] + [0] * (n - n // 2 - 1),
    }


def prover(candidate, spec: Spec) -> bool:
    if not isinstance(candidate, dict):
        return False
    width = candidate.get("width")
    initial = candidate.get("initial")
    if not isinstance(width, int) or not isinstance(initial, list):
        return False
    return len(initial) == width


def resolver(a, b):
    if a == b:
        return 0
    wa = a.get("width", 0)
    wb = b.get("width", 0)
    if wa == wb:
        return None
    return -1 if wa < wb else 1
