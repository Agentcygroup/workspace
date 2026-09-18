"""General computation: state_{t+1} = F(state_t, input_t)."""
from __future__ import annotations
from ..model import Spec


def solver(spec: Spec) -> dict:
    return {
        "state": {"phase": "init", "components": [c.name for c in spec.components]},
        "transition": "F",
    }


def prover(candidate, spec: Spec) -> bool:
    if not isinstance(candidate, dict):
        return False
    if "state" not in candidate or "transition" not in candidate:
        return False
    return isinstance(candidate["state"], dict)


def resolver(a, b):
    if a == b:
        return 0
    return None
