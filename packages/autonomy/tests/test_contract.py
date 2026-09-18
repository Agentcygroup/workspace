"""Autonomy contract enforcement tests."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "autonomy" / "src"))

from autonomy import load_contract, evaluate, Action, Context

CONTRACT = load_contract(ROOT / "security" / "autonomy_contract.yaml")
KILL_SWITCH = ROOT / "security" / "KILL_SWITCH"


@pytest.fixture(autouse=True)
def no_kill_switch():
    if KILL_SWITCH.exists():
        KILL_SWITCH.unlink()
    yield
    if KILL_SWITCH.exists():
        KILL_SWITCH.unlink()


class TestContractLoaded:
    def test_scopes_present(self):
        assert set(CONTRACT.scopes) == {"ops", "org", "infra"}

    def test_kill_switches_present(self):
        assert "ops.hold_all" in CONTRACT.kill_switches
        assert CONTRACT.kill_switches["org.hold_all"] is True


class TestScopeRefusals:
    def test_org_medium_refuses(self):
        a = Action("report", "org", "medium")
        d = evaluate(a, Context(), CONTRACT)
        assert d.allowed is False
        assert d.failed == "authorized"

    def test_infra_high_refuses(self):
        a = Action("apply_network_policy", "infra", "high")
        d = evaluate(a, Context(), CONTRACT)
        assert d.allowed is False
        assert d.failed == "authorized"

    def test_unknown_scope_refuses(self):
        a = Action("detect", "nonexistent", "low")
        d = evaluate(a, Context(), CONTRACT)
        assert d.allowed is False
        assert d.failed == "scope-or-level"


class TestAuthorized:
    def test_ops_low_detect_authorized(self):
        a = Action("detect", "ops", "low")
        d = evaluate(a, Context(), CONTRACT)
        assert d.allowed is True

    def test_ops_medium_rollback_with_conditions(self):
        a = Action("rollback", "ops", "medium")
        ctx = Context(confidence=0.95, blast_radius=2, reversibility="seconds")
        d = evaluate(a, ctx, CONTRACT)
        assert d.allowed is True


class TestKillSwitchFile:
    def test_kill_switch_file_blocks(self):
        KILL_SWITCH.parent.mkdir(parents=True, exist_ok=True)
        KILL_SWITCH.touch()
        a = Action("detect", "ops", "low")
        d = evaluate(a, Context(), CONTRACT)
        assert d.allowed is False
        assert d.failed == "kill_switch_file"
        KILL_SWITCH.unlink()


class TestCLI:
    def test_cli_org_medium_refuses(self):
        r = subprocess.run(
            [sys.executable, "-m", "autonomy.cli", "decide",
             "--scope", "org", "--level", "medium", "--action", "report"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert r.returncode == 1
        assert "not authorized" in r.stdout

    def test_cli_kill_switch_blocks(self):
        KILL_SWITCH.parent.mkdir(parents=True, exist_ok=True)
        KILL_SWITCH.touch()
        try:
            r = subprocess.run(
                [sys.executable, "-m", "autonomy.cli", "decide",
                 "--scope", "ops", "--level", "low", "--action", "detect"],
                cwd=ROOT, capture_output=True, text=True,
            )
            assert r.returncode == 1
            assert "kill switch" in r.stdout
        finally:
            KILL_SWITCH.unlink()
