"""Two-phase coordination between two autonomy decisions."""
from __future__ import annotations
from dataclasses import dataclass
from .evaluator import evaluate, Decision, Action, Context
from .contract import Contract


@dataclass(frozen=True)
class CoordinationResult:
    committed: bool
    reason: str
    decisions: tuple[Decision, ...]


def two_phase_commit(a: Action, b: Action, ctx_a: Context, ctx_b: Context,
                     contract: Contract) -> CoordinationResult:
    """Phase 1: both evaluate. Phase 2: commit only if both allow."""
    da = evaluate(a, ctx_a, contract)
    db = evaluate(b, ctx_b, contract)
    if da.allowed and db.allowed:
        return CoordinationResult(True, "both allowed", (da, db))
    failed = []
    if not da.allowed:
        failed.append(f"a: {da.reason}")
    if not db.allowed:
        failed.append(f"b: {db.reason}")
    return CoordinationResult(False, "; ".join(failed), (da, db))
