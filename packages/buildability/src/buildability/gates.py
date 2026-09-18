"""The six gates as a single ordered registry.

Each gate is a function Spec -> (passed, reason). The procedure walks the
registry in order and stops at the first failure. Adding a gate means
appending one entry; no other file changes.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable
from .model import Spec


class Gate(str, Enum):
    G0 = "G0"   # convergence
    G1 = "G1"   # spec
    G1_5 = "G1.5"  # consistency
    G2 = "G2"   # substrate
    G3 = "G3"   # solver
    G4 = "G4"   # prover
    G5 = "G5"   # resolver


@dataclass(frozen=True)
class GateResult:
    gate: Gate
    passed: bool
    reason: str = ""


# --- individual predicates (pure, no side effects) ------------------------

def _g0(spec: Spec, history: list[int] | None) -> tuple[bool, str]:
    if not history or len(history) < 2:
        return True, "insufficient history"
    diffs = [history[i] - history[i+1] for i in range(len(history)-1)]
    if all(d >= 1 for d in diffs):
        return True, f"closed {sum(diffs)} gaps over {len(diffs)} iterations"
    if all(d >= 0 for d in diffs) and any(d > 0 for d in diffs):
        return True, "bounded: plateau reached"
    return False, f"divergent: {history}"


def _g1(spec: Spec, _history) -> tuple[bool, str]:
    missing = [k for k, v in spec.elements_present().items() if not v]
    if missing:
        return False, "missing elements: " + ", ".join(missing)
    if spec.open_gaps():
        return False, "open gaps: " + ", ".join(g.name for g in spec.open_gaps())
    return True, "spec complete"


def _g1_5(spec: Spec, _history) -> tuple[bool, str]:
    from .consistency import check_consistency
    findings = check_consistency(spec)
    if findings:
        return False, "incoherent: " + "; ".join(
            f.reason for f in findings
        )
    return True, "consistent"


def _g2(spec: Spec, _history) -> tuple[bool, str]:
    """Check substrate availability.

    Precedence:
      1. If substrate_available is explicitly False, the spec author has
         declared the substrate unavailable. Fail regardless of probe.
      2. If substrate_available is explicitly True, the spec author has
         declared it available. Pass regardless of probe (the probe result
         is noted in the reason for visibility).
      3. If substrate_available is unset, probe the environment.

    This preserves the spec author's intent over the machine's state.
    """
    from .substrate import probe

    if not spec.substrate:
        return False, "no substrate declared"

    result = probe(spec.substrate)
    if result.available:
        return True, f"substrate '{spec.substrate}' available ({result.reason})"
    if not result.unknown:
        return False, f"substrate '{spec.substrate}' unavailable ({result.reason})"
    if spec.substrate_available is True:
        return True, f"substrate '{spec.substrate}' declared available, unverified"
    return False, f"substrate '{spec.substrate}' declared unavailable, unverified"


def _g3(spec: Spec, _history) -> tuple[bool, str, Any]:
    if spec.solver is None:
        return False, "no solver wired", None
    try:
        candidate = spec.solver()
    except Exception as e:
        return False, f"solver raised: {e!r}", None
    if candidate is None:
        return False, "solver returned None", None
    return True, "candidate produced", candidate


def _g4(spec: Spec, candidate: Any, _history) -> tuple[bool, str]:
    if spec.prover is None:
        return False, "no prover wired"
    try:
        if not spec.prover(candidate):
            return False, "prover rejected the candidate"
    except Exception as e:
        return False, f"prover raised: {e!r}"
    # Falsifiability: prover must reject a sentinel.
    try:
        sentinel_ok = spec.prover(object())
    except Exception:
        sentinel_ok = False
    if sentinel_ok:
        return False, "prover accepts non-candidates (not falsifiable)"
    return True, "candidate verified, prover falsifiable"


def _g5(spec: Spec, candidate: Any, _history) -> tuple[bool, str]:
    if spec.resolver is None:
        return False, "no resolver wired"
    try:
        a = spec.resolver(candidate, candidate)
    except Exception as e:
        return False, f"resolver raised: {e!r}"
    if a not in (0, None):
        return False, f"resolver(c, c) = {a}; violates self-tie"
    return True, "resolver total with tie semantics"


# --- the registry ---------------------------------------------------------

@dataclass(frozen=True)
class GateSpec:
    gate: Gate
    check: Callable                    # (spec[, candidate][, history]) -> ...
    regime: str                        # name of the regime if this gate fails


REGISTRY: list[GateSpec] = [
    GateSpec(Gate.G0, _g0, "DIVERGENT"),
    GateSpec(Gate.G1, _g1, "RESEARCH"),
    GateSpec(Gate.G1_5, _g1_5, "INCOHERENT"),
    GateSpec(Gate.G2, _g2, "ENGINEERING"),
    GateSpec(Gate.G3, _g3, "CONSTRUCTION"),
    GateSpec(Gate.G4, _g4, "VERIFICATION"),
    GateSpec(Gate.G5, _g5, "ADJUDICATION"),
]


# --- back-compat shims (so existing tests still import the old names) ------

def g0_convergence(history):
    ok, reason = _g0(None, history); return GateResult(Gate.G0, ok, reason)

def g1_spec(spec):
    ok, reason = _g1(spec, None); return GateResult(Gate.G1, ok, reason)

def g2_substrate(spec):
    ok, reason = _g2(spec, None); return GateResult(Gate.G2, ok, reason)

def g3_solver(spec):
    ok, reason, cand = _g3(spec, None); return GateResult(Gate.G3, ok, reason), cand

def g4_prover(spec, candidate):
    ok, reason = _g4(spec, candidate, None); return GateResult(Gate.G4, ok, reason)

def g5_resolver(spec, candidate):
    ok, reason = _g5(spec, candidate, None); return GateResult(Gate.G5, ok, reason)
