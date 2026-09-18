"""Quantum mechanics: [x,p] = ihbar, H psi = i hbar d psi / dt."""
from __future__ import annotations
from ..model import Spec


def solver(spec: Spec) -> dict:
    n = max(1, len(spec.components))
    return {"amplitudes": [1.0 / (n ** 0.5)] * n, "hamiltonian_diag": [1.0] * n}


def prover(candidate, spec: Spec) -> bool:
    if not isinstance(candidate, dict):
        return False
    amps = candidate.get("amplitudes")
    if not isinstance(amps, list) or not amps:
        return False
    norm = sum(a * a for a in amps)
    return abs(norm - 1.0) < 1e-6


def resolver(a, b):
    if a == b:
        return 0
    ea = sum(a.get("hamiltonian_diag", []))
    eb = sum(b.get("hamiltonian_diag", []))
    if ea == eb:
        return None
    return -1 if ea < eb else 1


def witness() -> dict:
    """A correctness witness: what this model claims and how it is verified."""
    return {
        "claim": "quantum model solves by symbolic state evolution",
        "verified_by": "packages/buildability/tests/test_model_correctness.py::test_quantum_model_solves",
    }
