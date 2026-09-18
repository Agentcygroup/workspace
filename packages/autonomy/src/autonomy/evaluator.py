"""The autonomy evaluator.

Given an Action and a Context, return a Decision. The Decision names
whether the action is allowed, which level authorized it, which
conditions were checked, and — if refused — which condition failed.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any
from .contract import Contract, ContractError
from .killswitch import read_kill_switches, any_active
from .blast import measure_blast_radius
from .audit import AuditLog


@dataclass(frozen=True)
class Action:
    name: str                       # e.g. "auto_scale"
    scope: str                      # e.g. "ops"
    level: str                      # e.g. "medium"
    blast_ceiling: int | None = None


@dataclass(frozen=True)
class Context:
    """Environment facts the evaluator uses.

    blast_radius default is 0, meaning "no effect known." Callers that
    perform real actions must supply a real measurement; -1 means
    "unmeasurable" and is refused.
    """
    confidence: float = 0.0
    blast_radius: int = 0
    reversibility: str = "unknown"   # seconds | minutes | hours | days | unknown
    audit_enabled: bool = True


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    checked: tuple[str, ...] = ()
    failed: str | None = None
    action: Action | None = None


COND_RE = re.compile(r"^(\w+)\s*(>=|<=|==|in)\s*(.+)$")


def _eval_condition(cond: str, ctx: Context) -> tuple[bool, str]:
    """Return (passed, reason). Unknown field -> fail."""
    m = COND_RE.match(cond.strip())
    if not m:
        return False, f"unparseable condition: {cond!r}"
    field, op, rhs = m.group(1), m.group(2), m.group(3).strip()

    if not hasattr(ctx, field):
        return False, f"unknown field {field!r} in condition {cond!r}"
    value = getattr(ctx, field)

    if op == ">=":
        try:
            return float(value) >= float(rhs), cond
        except (TypeError, ValueError):
            return False, cond
    if op == "<=":
        try:
            return float(value) <= float(rhs), cond
        except (TypeError, ValueError):
            return False, cond
    if op == "==":
        rhs_parsed = rhs
        if rhs in ("true", "false"):
            rhs_parsed = rhs == "true"
        return value == rhs_parsed, cond
    if op == "in":
        rhs_clean = rhs.strip("[]").replace(" ", "")
        options = tuple(x for x in rhs_clean.split(",") if x)
        return value in options, cond
    return False, cond


def evaluate(action: Action, ctx: Context, contract: Contract,
             audit: AuditLog | None = None) -> Decision:
    """Evaluate a proposed action. Every path returns a Decision.

    First check: the runtime kill switch file. If it exists, everything
    is refused, regardless of what the contract says. This runs before
    any other check, so no caller can bypass it.
    """
    checked: list[str] = []

    kill_switch_file = contract.kill_switch_file()
    if kill_switch_file.exists():
        checked.append("kill_switch_file")
        d = Decision(
            False,
            f"kill switch engaged: {kill_switch_file}",
            tuple(checked),
            "kill_switch_file",
            action,
        )
        if audit:
            audit.append({
                "action": action.name, "scope": action.scope,
                "level": action.level, "allowed": False,
                "reason": d.reason, "failed": d.failed,
            })
        return d

    # 1. Contract must know the scope and level.
    try:
        level = contract.level(action.scope, action.level)
    except ContractError as e:
        d = Decision(False, str(e), tuple(checked), "scope-or-level", action)
        if audit:
            audit.append({"action": action.name, "scope": action.scope,
                          "level": action.level, "allowed": False,
                          "reason": d.reason, "failed": d.failed})
        return d

    # 2. Kill switches.
    switches = read_kill_switches(contract)
    tripped, reason = any_active(level.kill_switches, switches)
    checked.append("kill_switch")
    if tripped:
        d = Decision(False, reason, tuple(checked), "kill_switch", action)
        if audit:
            audit.append({"action": action.name, "scope": action.scope,
                          "level": action.level, "allowed": False,
                          "reason": d.reason, "failed": d.failed})
        return d

    # 3. Action must be authorized at this level.
    checked.append("authorized")
    if action.name not in level.authorized:
        reason = (
            f"action {action.name!r} not authorized at "
            f"{action.scope}/{action.level}"
        )
        if level.reason:
            reason += f" ({level.reason})"
        d = Decision(False, reason, tuple(checked), "authorized", action)
        if audit:
            audit.append({"action": action.name, "scope": action.scope,
                          "level": action.level, "allowed": False,
                          "reason": d.reason, "failed": d.failed})
        return d

    # 4. Blast radius must not exceed the contract's ceiling for the action.
    ceiling = contract.blast_radius.get(action.name, -1)
    if ceiling >= 0:
        checked.append("blast_radius<=ceiling")
        if ctx.blast_radius < 0:
            d = Decision(False, "blast radius unmeasurable", tuple(checked),
                         "blast_radius<=ceiling", action)
            if audit:
                audit.append({"action": action.name, "scope": action.scope,
                              "level": action.level, "allowed": False,
                              "reason": d.reason, "failed": d.failed})
            return d
        if ctx.blast_radius > ceiling:
            reason = (
                f"blast radius {ctx.blast_radius} exceeds ceiling {ceiling} "
                f"for {action.name!r}"
            )
            d = Decision(False, reason, tuple(checked),
                         "blast_radius<=ceiling", action)
            if audit:
                audit.append({"action": action.name, "scope": action.scope,
                              "level": action.level, "allowed": False,
                              "reason": d.reason, "failed": d.failed})
            return d

    # 5. Every `requires` condition must pass.
    for cond in level.requires:
        checked.append(cond)
        passed, _ = _eval_condition(cond, ctx)
        if not passed:
            reason = f"condition failed: {cond}"
            d = Decision(False, reason, tuple(checked), cond, action)
            if audit:
                audit.append({"action": action.name, "scope": action.scope,
                              "level": action.level, "allowed": False,
                              "reason": d.reason, "failed": d.failed})
            return d

    # Allowed.
    d = Decision(True, "authorized", tuple(checked), None, action)
    if audit:
        audit.append({"action": action.name, "scope": action.scope,
                      "level": action.level, "allowed": True,
                      "reason": d.reason, "checked": list(checked)})
    return d
