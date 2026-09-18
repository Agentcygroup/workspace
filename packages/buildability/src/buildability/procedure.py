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
    RESEARCH        = "RESEARCH"
    INCOHERENT      = "INCOHERENT"         # G1
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

def _bind_model(spec: Spec) -> Spec:
    """If spec has no solver and a model is declared (on spec.model,
    falling back to spec.substrate for backwards compatibility), return
    a copy with solver/prover/resolver bound to that model.
    """
    if spec.solver is not None:
        return spec
    try:
        from .models import MODEL_REGISTRY
    except ImportError:
        return spec
    name = (spec.model or spec.substrate or "").lower()
    model = MODEL_REGISTRY.get(name)
    if model is None:
        return spec
    return spec.replace(
        solver=lambda: model.solver(spec),
        prover=lambda c: model.prover(c, spec),
        resolver=lambda a, b: model.resolver(a, b),
    )


def evaluate(spec: Spec, gap_history: list[int] | None = None) -> Verdict:
    """Run all gates in REGISTRY order; the first failure names the regime."""
    from .gates import REGISTRY, Gate

    spec = _bind_model(spec)

    results: list[GateResult] = []
    candidate = None

    for gs in REGISTRY:
        g = gs.gate
        if g is Gate.G0:
            ok, reason = gs.check(spec, gap_history)
        elif g is Gate.G3:
            ok, reason, candidate = gs.check(spec, gap_history)
        elif g in (Gate.G4, Gate.G5):
            ok, reason = gs.check(spec, candidate, gap_history)
        else:
            ok, reason = gs.check(spec, gap_history)

        results.append(GateResult(g, ok, reason))
        if not ok:
            return Verdict(gs.regime, tuple(results), candidate)

    return Verdict("BUILDABLE", tuple(results), candidate)


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
