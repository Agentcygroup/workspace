"""Regulation loop. Not a gate. A controller."""
from __future__ import annotations
from dataclasses import dataclass, field

from homeostasis import ALL_DRIVES, DriveVector, Refusal, evaluate


@dataclass
class RegulationTrace:
    steps: list = field(default_factory=list)
    terminal: str = ""


@dataclass
class RegulationResult:
    converged: bool
    final: DriveVector
    trace: RegulationTrace
    reason: str


def _error(dv, sp, d):
    return abs(dv.get(d) - sp.get(d))


def regulate(dv, setpoint, *, epsilon=0.01, step_size=0.1, max_steps=1000):
    sp_verdict = evaluate(setpoint)
    if not sp_verdict.allow:
        raise Refusal("homeostasis.setpoint.inadmissible",
                      "; ".join(sp_verdict.reasons))
    missing = [d for d in ALL_DRIVES if d not in dv.values]
    if missing:
        raise Refusal("homeostasis.state.missing", ", ".join(missing))

    trace = RegulationTrace()
    worst_drive = ""
    for _ in range(max_steps):
        errors = {d: _error(dv, setpoint, d) for d in ALL_DRIVES}
        worst_drive, worst_error = max(errors.items(), key=lambda kv: kv[1])
        if worst_error < epsilon:
            trace.terminal = "converged"
            return RegulationResult(
                converged=True, final=dv, trace=trace,
                reason=f"converged in {len(trace.steps)} steps",
            )
        before = dv.get(worst_drive)
        target = setpoint.get(worst_drive)
        # Never overshoot: if the target is within one step, land on it.
        if abs(target - before) <= step_size:
            after = target
        else:
            delta = step_size if target > before else -step_size
            after = max(0.0, min(1.0, before + delta))
        dv.set(worst_drive, after)
        trace.steps.append((worst_drive, before, after))

    trace.terminal = "budget-exhausted"
    return RegulationResult(
        converged=False, final=dv, trace=trace,
        reason=f"did not converge after {max_steps} steps; worst drive {worst_drive}",
    )


__all__ = ["regulate", "RegulationResult", "RegulationTrace"]
