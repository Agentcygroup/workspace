"""Gap history: close one gap at a time, track open-gap count."""
from __future__ import annotations
from typing import Callable
from .model import Spec, Gap


def close_one_gap(spec: Spec, resolver: Callable[[Gap], Gap | None] | None = None) -> Spec:
    open_gaps = spec.open_gaps()
    if not open_gaps:
        return spec
    target = open_gaps[0]
    resolved = resolver(target) if resolver else Gap(target.name, target.question, resolved=True)
    new_gaps = tuple(
        resolved if g is target else g
        for g in spec.gaps
    )
    return spec.replace(gaps=new_gaps)


def iterate(spec: Spec, max_iterations: int = 100) -> tuple[Spec, list[int]]:
    history = [len(spec.open_gaps())]
    for _ in range(max_iterations):
        if not spec.open_gaps():
            break
        before = len(spec.open_gaps())
        spec = close_one_gap(spec)
        after = len(spec.open_gaps())
        history.append(after)
        if after >= before:
            break
    return spec, history


def order_by_severity(spec: Spec) -> tuple[Gap, ...]:
    def score(g: Gap) -> int:
        q = g.question.lower()
        if "blocks" in q or "critical" in q:
            return 0
        if "may" in q or "nice" in q:
            return 2
        return 1
    return tuple(sorted(spec.open_gaps(), key=score))
