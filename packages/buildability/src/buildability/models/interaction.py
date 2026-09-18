"""Interaction combinators: gamma, delta, epsilon."""
from __future__ import annotations
from ..model import Spec


def solver(spec: Spec) -> dict:
    return {"nodes": ["gamma", "delta", "epsilon"], "edges": [], "spec": spec.name}


def prover(candidate, spec: Spec) -> bool:
    if not isinstance(candidate, dict):
        return False
    nodes = candidate.get("nodes")
    return isinstance(nodes, list) and all(
        n in ("gamma", "delta", "epsilon") for n in nodes
    )


def resolver(a, b):
    if a == b:
        return 0
    na = len(a.get("nodes", []))
    nb = len(b.get("nodes", []))
    if na == nb:
        return None
    return -1 if na < nb else 1
