"""Lambda calculus."""
from __future__ import annotations
from ..model import Spec


def solver(spec: Spec) -> dict:
    term = "lambda"
    for _ in spec.interfaces:
        term = f"(lambda x. {term})"
    return {"term": term, "interfaces": [i.name for i in spec.interfaces]}


def prover(candidate, spec: Spec) -> bool:
    if not isinstance(candidate, dict):
        return False
    if "term" not in candidate:
        return False
    return isinstance(candidate["term"], str)


def resolver(a, b):
    if a == b:
        return 0
    la = len(a.get("term", ""))
    lb = len(b.get("term", ""))
    if la == lb:
        return None
    return -1 if la < lb else 1
