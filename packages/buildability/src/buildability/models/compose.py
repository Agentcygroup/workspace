"""Compose two computational models into one."""
from __future__ import annotations
from dataclasses import dataclass
from . import MODEL_REGISTRY


@dataclass(frozen=True)
class ComposedModel:
    a: str
    b: str

    def solver(self, spec):
        return {"a": MODEL_REGISTRY[self.a].solver(spec),
                "b": MODEL_REGISTRY[self.b].solver(spec)}

    def prover(self, candidate, spec):
        return (MODEL_REGISTRY[self.a].prover(candidate, spec)
                and MODEL_REGISTRY[self.b].prover(candidate, spec))

    def resolver(self, x, y):
        return MODEL_REGISTRY[self.a].resolver(x, y)


def combine(a: str, b: str) -> ComposedModel:
    if a not in MODEL_REGISTRY:
        raise KeyError(f"unknown model: {a}")
    if b not in MODEL_REGISTRY:
        raise KeyError(f"unknown model: {b}")
    return ComposedModel(a, b)
