"""Per-element diagnostics for a Spec."""
from __future__ import annotations
from dataclasses import dataclass
from .model import Spec


@dataclass(frozen=True)
class Diagnostic:
    element: str
    state: str
    hint: str


def diagnose(spec: Spec) -> tuple[Diagnostic, ...]:
    out = []

    if not spec.components:
        out.append(Diagnostic("components", "empty", "declare at least one component"))
    else:
        for c in spec.components:
            if not c.name:
                out.append(Diagnostic("components", "incomplete",
                                      f"component {c.responsibility!r} has no name"))
            if not c.responsibility:
                out.append(Diagnostic("components", "incomplete",
                                      f"component {c.name!r} has no responsibility"))

    if not spec.interfaces:
        out.append(Diagnostic("interfaces", "empty", "declare at least one interface"))
    else:
        for i in spec.interfaces:
            for field in ("name", "schema", "protocol", "version", "failure_semantics"):
                if not getattr(i, field):
                    out.append(Diagnostic("interfaces", "incomplete",
                                          f"interface {i.name!r} missing {field}"))

    if not spec.invariants:
        out.append(Diagnostic("invariants", "empty", "declare at least one invariant"))
    else:
        for v in spec.invariants:
            if not v.predicate:
                out.append(Diagnostic("invariants", "incomplete",
                                      f"invariant {v.name!r} has no predicate"))

    if spec.lifecycle is None:
        out.append(Diagnostic("lifecycle", "empty", "declare a lifecycle"))
    else:
        for field in ("create", "update", "migrate", "delete", "rollback"):
            if not getattr(spec.lifecycle, field):
                out.append(Diagnostic("lifecycle", "incomplete",
                                      f"lifecycle missing {field}"))

    if not spec.substrate:
        out.append(Diagnostic("substrate", "empty", "declare a substrate"))

    for g in spec.open_gaps():
        out.append(Diagnostic("gaps", "open", f"gap {g.name!r}: {g.question}"))

    return tuple(out)
