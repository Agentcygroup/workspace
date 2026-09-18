"""Blast-radius measurement.

Given an action and the current cluster state, return the number of
resources the action could affect if it succeeds, or -1 if the radius
cannot be measured.

The default measurer is conservative: if the action class is in the
contract's blast_radius table, use the ceiling. Real deployments would
substitute a measurer that inspects live state.
"""
from __future__ import annotations
from .contract import Contract


def measure_blast_radius(action_name: str, contract: Contract) -> int:
    return contract.blast_radius.get(action_name, -1)


def exceeds_ceiling(action_name: str, ceiling: int, contract: Contract) -> bool:
    r = measure_blast_radius(action_name, contract)
    if r < 0:
        return True  # unmeasurable is treated as exceeding
    return r > ceiling
