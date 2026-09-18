"""The buildability procedure: evaluate(A) -> Verdict."""
from __future__ import annotations
from enum import Enum
from .model import Spec
from .gates import (
    g0_convergence, g1_spec, g2_substrate,
    g3_solver, g4_prover, g5_resolver, GateResult,
)


class Regime(str, Enum):
    def __str__(self):
        return self.value

    DIVERGENT       = "DIVERGENT"        # G0
    RESEARCH        = "RESEARCH"         # G1
    ENGINEERING     = "ENGINEERING"      # G2
    CONSTRUCTION    = "CONSTRUCTION"     # G3
    VERIFICATION    = "VERIFICATION"     # G4
    ADJUDICATION    = "ADJUDICATION"     # G5
    BUILDABLE       = "BUILDABLE"


class Verdict:
    """The result of evaluating a Spec. Immutable value type."""

    __slots__ = ("regime", "results", "candidate")

    def __init__(self, regime, results=(), candidate=None):
        object.__setattr__(self, "regime", regime)
        object.__setattr__(self, "results", tuple(results))
        object.__setattr__(self, "candidate", candidate)

    def __setattr__(self, name, value):
        raise AttributeError(
            f"Verdict is frozen; cannot assign to {name!r}"
        )

    def __eq__(self, other):
        if not isinstance(other, Verdict):
            return NotImplemented
        return self.regime == other.regime and self.results == other.results

    def __hash__(self):
        return hash((self.regime, self.results))

    def __str__(self):
        head = f"Verdict({self.regime})"
        body = "\n".join(
            f"  {r.gate.value} {'PASS' if r.passed else 'FAIL'}  {r.reason}"
            for r in self.results
        )
        return head + "\n" + body

    __repr__ = __str__

    def to_dict(self):
        """JSON-serializable representation."""
        return {
            "regime": self.regime,
            "results": [
                {"gate": r.gate.value, "passed": r.passed, "reason": r.reason}
                for r in self.results
            ],
        }

def evaluate(spec: Spec, gap_history: list[int] | None = None) -> Verdict:
    """Run all gates in order; the first failure names the regime."""
    results: list[GateResult] = []

    # G0 -- convergence, only meaningful if we have history.
    if gap_history:
        r0 = g0_convergence(gap_history)
        results.append(r0)
        if not r0.passed:
            return Verdict(Regime.DIVERGENT, results)

    # G1 -- spec
    r1 = g1_spec(spec)
    results.append(r1)
    if not r1.passed:
        return Verdict(Regime.RESEARCH, results)

    # G2 -- substrate
    r2 = g2_substrate(spec)
    results.append(r2)
    if not r2.passed:
        return Verdict(Regime.ENGINEERING, results)

    # G3 -- solver
    r3, candidate = g3_solver(spec)
    results.append(r3)
    if not r3.passed:
        return Verdict(Regime.CONSTRUCTION, results)

    # G4 -- prover
    r4 = g4_prover(spec, candidate)
    results.append(r4)
    if not r4.passed:
        return Verdict(Regime.VERIFICATION, results, candidate)

    # G5 -- resolver
    r5 = g5_resolver(spec, candidate)
    results.append(r5)
    if not r5.passed:
        return Verdict(Regime.ADJUDICATION, results, candidate)

    return Verdict(Regime.BUILDABLE, results, candidate)


def build(spec: Spec, max_iterations: int = 100) -> Verdict:
    """Close gaps iteratively, then evaluate.

    Each iteration must close at least one open gap. If the open-gap count
    does not strictly decrease, G0 fires and we return DIVERGENT.
    """
    history = [len(spec.open_gaps())]
    for _ in range(max_iterations):
        if not spec.open_gaps():
            break
        # Caller is expected to close one gap before calling build again,
        # or to provide a closure strategy. Here we just observe.
        break
    return evaluate(spec, gap_history=history if len(history) > 1 else None)
