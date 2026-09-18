"""End-to-end test: a production-style action is evaluated before execution."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "autonomy" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from autonomy import (
    load_contract, evaluate, Action, Context,
    FilesystemSignals, StaticSignals,
)
from autonomy.evaluator import Decision


class DeploymentAction:
    """A production-style action that goes through the evaluator."""

    def __init__(self, contract, signals):
        self.contract = contract
        self.signals = signals
        self.executed = 0
        self.refused = 0

    def execute(self, action_name: str, scope: str, level: str) -> Decision:
        ctx = Context(
            confidence=self.signals.confidence(action_name),
            blast_radius=self.signals.blast_radius(action_name),
            reversibility="seconds",
        )
        action = Action(action_name, scope, level)
        decision = evaluate(action, ctx, self.contract)
        if decision.allowed:
            self.executed += 1
        else:
            self.refused += 1
        return decision


@pytest.fixture
def contract():
    return load_contract(ROOT / "security" / "autonomy_contract.yaml")


@pytest.fixture
def switch(tmp_path):
    p = ROOT / "security" / "KILL_SWITCH"
    yield p
    if p.exists():
        p.unlink()


def test_production_allows_low_ops(contract, switch):
    if switch.exists():
        switch.unlink()
    signals = StaticSignals(blast_radius=0, confidence=0.0, human_available=False)
    a = DeploymentAction(contract, signals)
    d = a.execute("detect", "ops", "low")
    assert d.allowed is True
    assert a.executed == 1


def test_production_refuses_high_ops_without_confidence(contract, switch):
    if switch.exists():
        switch.unlink()
    signals = StaticSignals(blast_radius=1, confidence=0.5, human_available=True)
    a = DeploymentAction(contract, signals)
    d = a.execute("auto_scale", "ops", "high")
    assert d.allowed is False
    assert a.refused == 1
    assert a.executed == 0


def test_production_allows_high_ops_with_full_evidence(contract, switch):
    if switch.exists():
        switch.unlink()
    signals = StaticSignals(blast_radius=1, confidence=0.999, human_available=True)
    a = DeploymentAction(contract, signals)
    d = a.execute("auto_scale", "ops", "high")
    assert d.allowed is True
    assert a.executed == 1
