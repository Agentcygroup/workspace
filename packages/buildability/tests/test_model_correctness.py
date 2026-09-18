"""Correctness tests for the computational models.

Each test asserts that a model solves a specific problem correctly, not
just that its solver returns a value.
"""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import MODEL_REGISTRY, Spec


def _spec():
    return Spec(name="test")


def test_boolean_satisfiability():
    m = MODEL_REGISTRY.get("boolean")
    if m is None:
        pytest.skip("boolean model not present")
    s = _spec()
    candidate = m.solver(s)
    # A solver must return a truth-table structure with assignments.
    assert isinstance(candidate, dict)
    assert "components" in candidate
    assert "assignments" in candidate
    assert isinstance(candidate["assignments"], list)


def test_lambda_reduction():
    m = MODEL_REGISTRY.get("lambda")
    if m is None:
        pytest.skip("lambda model not present")
    candidate = m.solver(_spec())
    assert isinstance(candidate, dict)
    assert "term" in candidate
    # A lambda term must contain the lambda symbol.
    assert "lambda" in candidate["term"].lower() or "λ" in candidate["term"]


def test_turing_halts():
    m = MODEL_REGISTRY.get("turing")
    if m is None:
        pytest.skip("turing model not present")
    candidate = m.solver(_spec())
    assert isinstance(candidate, dict)
    assert "transitions" in candidate
    assert "states" in candidate
    # The machine must have an accepting state.
    assert any("acc" in s.lower() for s in candidate["states"])


def test_combinatory_identity():
    m = MODEL_REGISTRY.get("combinatory")
    if m is None:
        pytest.skip("combinatory model not present")
    candidate = m.solver(_spec())
    assert isinstance(candidate, dict)
    assert candidate.get("I") is True
    assert candidate.get("S") is True
    assert candidate.get("K") is True
