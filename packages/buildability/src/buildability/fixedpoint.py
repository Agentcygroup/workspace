"""Fixed-point test: S(A) is closed when adding detail does not change the build."""
from __future__ import annotations
from typing import Any, Callable
from .model import Spec


def is_fixed_point(spec: Spec, perturbations: list[Callable[[Spec], Spec]]) -> bool:
    """Return True iff no perturbation changes the solver's output.

    perturbations are functions that add detail to the spec. If the solver
    output is identical under every perturbation, the spec is at fixed point.
    """
    if spec.solver is None:
        raise ValueError("spec has no solver; cannot test fixed point")
    base = spec.solver()
    for perturb in perturbations:
        variant = perturb(spec)
        try:
            out = variant.solver() if variant.solver else spec.solver()
        except Exception:
            return False
        if out != base:
            return False
    return True


def closure(spec: Spec,
            perturbations: list[Callable[[Spec], Spec]],
            max_rounds: int = 100) -> tuple[Spec, int]:
    """Iterate until fixed point or max_rounds. Returns (spec, rounds)."""
    for r in range(1, max_rounds + 1):
        if is_fixed_point(spec, perturbations):
            return spec, r
        # Caller-supplied perturb functions may mutate; if none sticks, bail.
        changed = False
        for perturb in perturbations:
            before = len(spec.gaps)
            spec = perturb(spec)
            if len(spec.gaps) != before:
                changed = True
                break
        if not changed:
            return spec, r
    return spec, max_rounds
