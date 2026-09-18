"""Specification model: the six elements a complete S(A) must contain."""
from __future__ import annotations
from dataclasses import dataclass, replace as _dc_replace
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class Component:
    name: str
    responsibility: str

    def complete(self) -> bool:
        return bool(self.name) and bool(self.responsibility)


@dataclass(frozen=True)
class Interface:
    name: str
    schema: str
    protocol: str
    version: str
    failure_semantics: str

    def complete(self) -> bool:
        return all([self.name, self.schema, self.protocol,
                    self.version, self.failure_semantics])


@dataclass(frozen=True)
class Invariant:
    name: str
    predicate: str          # human-readable statement
    check: Optional[Callable[[Any], bool]] = None

    def complete(self) -> bool:
        return bool(self.name) and bool(self.predicate)


@dataclass(frozen=True)
class Lifecycle:
    create: str
    update: str
    migrate: str
    delete: str
    rollback: str

    def complete(self) -> bool:
        return all([self.create, self.update, self.migrate,
                    self.delete, self.rollback])


@dataclass(frozen=True)
class Gap:
    name: str
    question: str           # the open decision, explicitly named
    resolved: bool = False

    def is_open(self) -> bool:
        return not self.resolved


@dataclass(frozen=True)
class Spec:
    """A specification S(A).

    Frozen: any change to a Spec produces a new Spec via `replace`.
    This is what makes the fixed-point loop in closure() provably
    side-effect free.
    """

    def replace(self, **changes) -> "Spec":
        """Return a new Spec with the given fields replaced.

        Collection fields must be tuples. Passing a list is a TypeError
        rather than a silent coercion, so callers cannot accidentally
        reintroduce mutable state.
        """
        collection_fields = {"components", "interfaces", "invariants", "gaps"}
        for k, v in changes.items():
            if k in collection_fields and not isinstance(v, tuple):
                raise TypeError(
                    f"Spec.{k} must be a tuple, got {type(v).__name__}"
                )
        return _dc_replace(self, **changes)
    name: str
    components: tuple[Component, ...] = ()
    interfaces: tuple[Interface, ...] = ()
    invariants: tuple[Invariant, ...] = ()
    lifecycle: Optional[Lifecycle] = None
    substrate: Optional[str] = None
    substrate_available: bool = False
    gaps: tuple[Gap, ...] = ()

    # Solver / prover / resolver wiring (optional, set by caller).
    solver: Optional[Callable[[], Any]] = None
    prover: Optional[Callable[[Any], bool]] = None
    resolver: Optional[Callable[[Any, Any], Optional[int]]] = None

    # ---- spec-completeness (G1) -------------------------------------------
    def open_gaps(self) -> list[Gap]:
        return [g for g in self.gaps if g.is_open()]

    def elements_present(self) -> dict[str, bool]:
        return {
            "components": bool(self.components) and all(c.complete() for c in self.components),
            "interfaces": bool(self.interfaces) and all(i.complete() for i in self.interfaces),
            "invariants": bool(self.invariants) and all(v.complete() for v in self.invariants),
            "lifecycle":  self.lifecycle is not None and self.lifecycle.complete(),
            "substrate":  bool(self.substrate),
            "gaps":       True,   # gaps may be present-and-named; that is fine
        }

    def spec_complete(self) -> bool:
        """G1: all six elements present AND no open gaps."""
        return all(self.elements_present().values()) and not self.open_gaps()

    def gap_free(self) -> bool:
        return not self.open_gaps()
