"""Buildability framework.

A is buildable iff  S(A) ∧ Σ ∧ Solver ∧ Prover ∧ Resolver,
and the process that produces S(A) converges.

Gates:
    G0 Convergence    gaps closed >= gaps opened per iteration
    G1 Spec           components, interfaces, invariants, lifecycle, substrate, gaps
    G2 Substrate      target platform exists and is reachable
    G3 Solver         a candidate artifact is produced
    G4 Prover         a falsifiable check exists that fails on non-A
    G5 Resolver       a total, antisymmetric, transitive order with ⊥ on ties
"""

from .model import Spec, Component, Interface, Invariant, Lifecycle, Gap
from .gates import (
    Gate, GateResult,
    g0_convergence, g1_spec, g2_substrate,
    g3_solver, g4_prover, g5_resolver,
)
from .procedure import evaluate, build, Verdict, Regime
from .compose import evaluate_many, CompositionResult, InterfaceMismatch
from .models import MODEL_REGISTRY
from .substrate import probe, ProbeResult
from .loader import spec_from_dict, spec_from_file
from .fixedpoint import is_fixed_point, closure
from .intent import IntentRatio

__all__ = [
    "Spec", "Component", "Interface", "Invariant", "Lifecycle", "Gap",
    "Gate", "GateResult",
    "g0_convergence", "g1_spec", "g2_substrate",
    "g3_solver", "g4_prover", "g5_resolver",
    "evaluate", "build", "Verdict", "Regime",
    "evaluate_many", "CompositionResult", "InterfaceMismatch",
    "MODEL_REGISTRY", "probe", "ProbeResult",
    "is_fixed_point", "closure",
    "IntentRatio",
]
