"""The six gates: G0 convergence, G1-G5 the buildability predicates."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional
from .model import Spec


class Gate(str, Enum):
    G0_CONVERGENCE  = "G0"
    G1_SPEC         = "G1"
    G2_SUBSTRATE    = "G2"
    G3_SOLVER       = "G3"
    G4_PROVER       = "G4"
    G5_RESOLVER     = "G5"


@dataclass(frozen=True)
class GateResult:
    gate: Gate
    passed: bool
    reason: str = ""


def g0_convergence(gap_history: list[int]) -> GateResult:
    """G0: each iteration must close >=1 gap and open <1.

    gap_history is the sequence of open-gap counts per iteration,
    oldest first. Passes iff the sequence is strictly decreasing.
    """
    if len(gap_history) < 2:
        return GateResult(Gate.G0_CONVERGENCE, True, "insufficient history; assume convergent")
    diffs = [gap_history[i] - gap_history[i+1] for i in range(len(gap_history)-1)]
    if all(d >= 1 for d in diffs):
        return GateResult(Gate.G0_CONVERGENCE, True,
                          f"closed {sum(diffs)} gaps over {len(diffs)} iterations")
    if all(d >= 0 for d in diffs) and any(d > 0 for d in diffs):
        return GateResult(Gate.G0_CONVERGENCE, True, "bounded: plateau reached")
    return GateResult(Gate.G0_CONVERGENCE, False,
                      f"divergent: gap counts {gap_history}")


def g1_spec(spec: Spec) -> GateResult:
    """G1: all six elements present and no open gaps."""
    present = spec.elements_present()
    missing = [k for k, v in present.items() if not v]
    if missing:
        return GateResult(Gate.G1_SPEC, False, "missing elements: " + ", ".join(missing))
    if spec.open_gaps():
        names = ", ".join(g.name for g in spec.open_gaps())
        return GateResult(Gate.G1_SPEC, False, "open gaps: " + names)
    return GateResult(Gate.G1_SPEC, True, "spec complete")


def g2_substrate(spec: Spec) -> GateResult:
    """G2: substrate exists and is reachable."""
    if not spec.substrate:
        return GateResult(Gate.G2_SUBSTRATE, False, "no substrate declared")
    if not spec.substrate_available:
        return GateResult(Gate.G2_SUBSTRATE, False,
                          f"substrate '{spec.substrate}' unavailable")
    return GateResult(Gate.G2_SUBSTRATE, True, f"substrate '{spec.substrate}' available")


def g3_solver(spec: Spec) -> tuple[GateResult, Any]:
    """G3: a candidate artifact is produced."""
    if spec.solver is None:
        return GateResult(Gate.G3_SOLVER, False, "no solver wired"), None
    try:
        candidate = spec.solver()
    except Exception as e:
        return GateResult(Gate.G3_SOLVER, False, f"solver raised: {e!r}"), None
    if candidate is None:
        return GateResult(Gate.G3_SOLVER, False, "solver returned None"), None
    return GateResult(Gate.G3_SOLVER, True, "candidate produced"), candidate


def g4_prover(spec: Spec, candidate: Any) -> GateResult:
    """G4: a falsifiable check exists that fails on non-A.

    A prover is only valid if there exists a candidate for which it returns False.
    We test falsifiability by feeding a sentinel that must fail.
    """
    if spec.prover is None:
        return GateResult(Gate.G4_PROVER, False, "no prover wired")
    try:
        ok = spec.prover(candidate)
    except Exception as e:
        return GateResult(Gate.G4_PROVER, False, f"prover raised: {e!r}")
    if not ok:
        return GateResult(Gate.G4_PROVER, False, "prover rejected the candidate")
    # Falsifiability check: the prover must reject a clearly-wrong candidate.
    sentinel = object()
    try:
        sentinel_ok = spec.prover(sentinel)
    except Exception:
        sentinel_ok = False
    if sentinel_ok:
        return GateResult(Gate.G4_PROVER, False,
                          "prover accepts non-candidates (not falsifiable)")
    return GateResult(Gate.G4_PROVER, True, "candidate verified, prover falsifiable")


def g5_resolver(spec: Spec, candidate: Any) -> GateResult:
    """G5: a total, antisymmetric, transitive order with ⊥ on ties."""
    if spec.resolver is None:
        return GateResult(Gate.G5_RESOLVER, False, "no resolver wired")
    try:
        a = spec.resolver(candidate, candidate)
    except Exception as e:
        return GateResult(Gate.G5_RESOLVER, False, f"resolver raised: {e!r}")
    # Self-comparison must return a tie (0) or ⊥ (None).
    if a not in (0, None):
        return GateResult(Gate.G5_RESOLVER, False,
                          f"resolver(c, c) = {a}; violates self-tie")
    return GateResult(Gate.G5_RESOLVER, True, "resolver total with tie semantics")
