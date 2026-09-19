"""§15: metaphor compression.

Given a high-dimensional state, find a symbol whose embedding is
within ε of it; if none exists, register one whose expansion is the
state's decomposition.
"""
from __future__ import annotations
import math
from .schema import Symbol, Expansion, SYMBOL_TABLE


def _dist(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return float("inf")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def find_symbol_for(state_embedding: list[float], eps: float = 0.05) -> Symbol | None:
    best, best_d = None, float("inf")
    for s in SYMBOL_TABLE.values():
        d = _dist(s.embedding, state_embedding)
        if d < best_d:
            best, best_d = s, d
    if best is None or best_d >= eps:
        return None
    return best


def decompose(state: dict) -> Expansion:
    """Turn a state dict into an expansion: its keys are operators,
    its values are constraints."""
    ops = tuple(state.get("operators", ()))
    constraints = {k: v for k, v in state.items() if k != "operators"}
    return Expansion(operators=ops, constraints=constraints)


def compress(state_id: str, state_embedding: list[float],
             state: dict, eps: float = 0.05) -> Symbol:
    """§15 SYMBOL_COMPRESSION. Idempotent: if a symbol already fits,
    return it; otherwise register a new one."""
    existing = find_symbol_for(state_embedding, eps)
    if existing is not None:
        return existing
    sym = Symbol(id=state_id, embedding=list(state_embedding),
                 expands_to=decompose(state))
    SYMBOL_TABLE[state_id] = sym
    return sym
