"""Boolean logic via NAND."""
from __future__ import annotations
from ..model import Spec


def NAND(x, y): return not (x and y)
def NOT(x): return NAND(x, x)
def AND(x, y): return NAND(NAND(x, y), NAND(x, y))
def OR(x, y): return NAND(NAND(x, x), NAND(y, y))
def XOR(x, y): return NAND(NAND(x, NAND(x, y)), NAND(y, NAND(x, y)))


def solver(spec: Spec) -> dict:
    comps = [c.name for c in spec.components]
    n = len(comps)
    rows = []
    for i in range(2 ** n):
        rows.append({name: bool((i >> j) & 1) for j, name in enumerate(comps)})
    return {"components": comps, "assignments": rows}


def prover(candidate, spec: Spec) -> bool:
    if not isinstance(candidate, dict):
        return False
    if "components" not in candidate:
        return False
    return set(candidate["components"]) == {c.name for c in spec.components}


def resolver(a, b):
    if a == b:
        return 0
    if not isinstance(a, dict) or not isinstance(b, dict):
        return None
    na = len(a.get("assignments", []))
    nb = len(b.get("assignments", []))
    return -1 if na < nb else 1
