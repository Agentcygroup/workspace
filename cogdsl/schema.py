"""§1-§7: types, structs, registries.

Every struct here is a frozen dataclass. The registries are module-level
dicts. `any` in the schema becomes `object` in Python; the type checker
is not the runtime check. Runtime checks live in invariants.py.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time


Vector = list[float]
Probability = float
Timestamp = int
AttributeMap = dict[str, Any]
ConstraintMap = dict[str, Any]
StateMap = dict[str, Any]


# §2 Symbol table --------------------------------------------------------

@dataclass(frozen=True)
class Expansion:
    operators: tuple[str, ...] = ()
    constraints: ConstraintMap = field(default_factory=dict)
    default_params: AttributeMap = field(default_factory=dict)


@dataclass(frozen=True)
class Symbol:
    id: str
    embedding: Vector = ()
    expands_to: Expansion = field(default_factory=Expansion)
    aliases: tuple[str, ...] = ()


# §3 Intent --------------------------------------------------------------

@dataclass(frozen=True)
class Intent:
    id: str
    raw_input: str
    symbols: tuple[str, ...]
    context: str = ""
    priority: int = 0


# §4 Context -------------------------------------------------------------

@dataclass(frozen=True)
class Event:
    ts: Timestamp
    type: str
    payload: AttributeMap = field(default_factory=dict)


@dataclass
class Context:
    id: str
    entities: list[str] = field(default_factory=list)
    environment: StateMap = field(default_factory=dict)
    history: list[Event] = field(default_factory=list)

    def record(self, kind: str, payload: AttributeMap | None = None) -> None:
        self.history.append(Event(ts=int(time.time() * 1000),
                                  type=kind, payload=payload or {}))


# §5 Entity + Tracking ---------------------------------------------------

@dataclass
class Entity:
    id: str
    cls: str
    attributes: AttributeMap = field(default_factory=dict)
    state: StateMap = field(default_factory=dict)
    belief: Probability = 0.5
    last_seen: Timestamp = 0


@dataclass(frozen=True)
class Observation:
    ts: Timestamp
    features: Vector
    source: str = ""


@dataclass
class Track:
    entity_id: str
    observations: list[Observation] = field(default_factory=list)
    continuity_score: Probability = 0.0


# §6 Operator ------------------------------------------------------------

@dataclass(frozen=True)
class Operator:
    id: str
    input_schema: AttributeMap = field(default_factory=dict)
    output_schema: AttributeMap = field(default_factory=dict)
    preconditions: ConstraintMap = field(default_factory=dict)
    effects: StateMap = field(default_factory=dict)
    callable_name: str = ""    # resolves at runtime via OPERATOR_BACKENDS


# §7 Exec graph ----------------------------------------------------------

class Status(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass
class ExecNode:
    id: str
    operator: str
    inputs: AttributeMap = field(default_factory=dict)
    outputs: AttributeMap = field(default_factory=dict)
    status: Status = Status.PENDING


@dataclass(frozen=True)
class ExecEdge:
    from_: str
    to: str
    condition: ConstraintMap = field(default_factory=dict)


@dataclass
class ExecGraph:
    nodes: list[ExecNode] = field(default_factory=list)
    edges: list[ExecEdge] = field(default_factory=list)


# Registries -------------------------------------------------------------

SYMBOL_TABLE: dict[str, Symbol] = {}
OPERATOR_TABLE: dict[str, Operator] = {}
OPERATOR_BACKENDS: dict[str, callable] = {}
