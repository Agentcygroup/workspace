"""Autonomy: declarative delegation with runtime enforcement.

Given a proposed action and its context, decide whether to permit it.
Every decision is recorded. Every refusal names the failing condition.
"""
from .contract import Contract, load_contract
from .evaluator import evaluate, Decision, Action, Context
from .killswitch import KillSwitch, read_kill_switches
from .blast import measure_blast_radius
from .audit import AuditLog

__all__ = [
    "Contract", "load_contract",
    "evaluate", "Decision", "Action", "Context",
    "KillSwitch", "read_kill_switches",
    "measure_blast_radius",
    "AuditLog",
]
