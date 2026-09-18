"""Intent-ratio: the four components that bound buildability."""
from __future__ import annotations
from dataclasses import dataclass
from .model import Spec


@dataclass
class IntentRatio:
    spec_debt: float            # fraction of S(A) still open
    prover_coverage: float      # fraction of invariants with a check
    resolver_determinacy: float # fraction of interface pairs the resolver orders
    convergence_rate: float     # gaps closed per iteration

    def closed(self) -> bool:
        return (self.spec_debt == 0.0
                and self.prover_coverage == 1.0
                and self.resolver_determinacy == 1.0
                and self.convergence_rate >= 1.0)

    @classmethod
    def measure(cls, spec: Spec, gap_history: list[int]) -> "IntentRatio":
        total = len(spec.gaps) or 1
        open_ = len(spec.open_gaps())
        spec_debt = open_ / total

        inv_total = len(spec.invariants) or 1
        inv_checked = sum(1 for i in spec.invariants if i.check is not None)
        prover_coverage = inv_checked / inv_total

        # Resolver determinacy is 1.0 if a resolver is wired, else 0.0.
        resolver_determinacy = 1.0 if spec.resolver is not None else 0.0

        if len(gap_history) >= 2:
            closed = gap_history[0] - gap_history[-1]
            convergence_rate = closed / (len(gap_history) - 1)
        else:
            convergence_rate = 1.0
        return cls(spec_debt, prover_coverage, resolver_determinacy, convergence_rate)
