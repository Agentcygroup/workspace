"""Fixed-point test: S(A) is closed when adding detail does not change the build.

`Spec` is frozen. Perturbations are pure functions Spec -> Spec. `closure`
never mutates; it returns a new Spec plus the number of rounds it took to
reach a fixed point (or max_rounds if it did not).
"""
from __future__ import annotations
from typing import Callable
from .model import Spec


Perturbation = Callable[[Spec], Spec]


def is_fixed_point(spec: Spec, perturbations: list[Perturbation]) -> bool:
    """Return True iff no perturbation changes the solver's output.

    The spec is at a fixed point for these perturbations when every
    perturbation produces a variant whose solver output equals the base
    output. If the spec has no solver, we compare spec identity instead:
    a perturbation that returns a spec equal to the input does not move
    the fixed point.
    """
    if spec.solver is not None:
        base = spec.solver()
        for perturb in perturbations:
            variant = perturb(spec)
            if variant.solver is None:
                # Perturbation dropped the solver; treat as non-fixed.
                return False
            try:
                out = variant.solver()
            except Exception:
                return False
            if out != base:
                return False
        return True

    # No solver: use structural equality of the produced spec.
    for perturb in perturbations:
        variant = perturb(spec)
        if variant != spec:
            return False
    return True


def closure(
    spec: Spec,
    perturbations: list[Perturbation],
    max_rounds: int = 100,
) -> tuple[Spec, int]:
    """Iterate until fixed point or max_rounds.

    Returns (spec_at_fixed_point, rounds_taken). Never mutates the input.

    Termination rule: each round must strictly reduce the number of open
    gaps, OR must not change the spec at all. If a round leaves the spec
    unchanged and the fixed-point test fails, we stop early and return
    what we have -- that is a divergent perturbation set, not a bug.
    """
    for r in range(1, max_rounds + 1):
        if is_fixed_point(spec, perturbations):
            return spec, r

        prev = spec
        for perturb in perturbations:
            candidate = perturb(spec)
            if candidate.open_gaps() < spec.open_gaps() or candidate != spec:
                spec = candidate
                break
        if spec == prev:
            # Nothing moved; perturbation set is divergent.
            return spec, r

    return spec, max_rounds
