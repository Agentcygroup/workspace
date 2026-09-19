"""Public API. §19 MINIMAL RUNTIME INTERFACE.

  REGISTER_SYMBOL      -> register_symbol
  REGISTER_OPERATOR    -> register_operator
  INGEST_INTENT        -> ingest_intent
  RUN                  -> run
  UPDATE_OBSERVATION   -> update_observation

Hooks §20:
  SYMBOL_RESOLVER      -> cogdsl.symbols  (replaceable)
  GRAPH_OPTIMIZER      -> cogdsl.compiler.GRAPH_OPTIMIZER
  TRACKING_MODEL       -> cogdsl.tracking.TRACKING_MODEL
  OPERATOR_BACKENDS    -> cogdsl.schema.OPERATOR_BACKENDS
"""
from __future__ import annotations
from .schema import (
    Symbol, Expansion, Intent, Context, Event, Entity, Observation, Track,
    Operator, ExecNode, ExecEdge, ExecGraph, Status,
    SYMBOL_TABLE, OPERATOR_TABLE, OPERATOR_BACKENDS,
)
from .symbols import register_symbol, resolve_symbols
from .compiler import compile_intent, GRAPH_OPTIMIZER as _GO
from .engine import execute, ExecTrace, check_preconditions
from .tracking import update_track, TRACKING_MODEL as _TM
from .compression import compress, find_symbol_for
from . import invariants


def register_operator(op: Operator, backend=None) -> None:
    """§19 REGISTER_OPERATOR. If a backend is provided, it is bound by op.id."""
    OPERATOR_TABLE[op.id] = op
    if backend is not None:
        OPERATOR_BACKENDS[op.id] = backend


def ingest_intent(intent: Intent) -> ExecGraph:
    """§19 INGEST_INTENT."""
    return compile_intent(intent)


def run(graph: ExecGraph, ctx: Context) -> ExecTrace:
    """§19 RUN."""
    return execute(graph, ctx)


def update_observation(track: Track, obs: Observation) -> Track:
    """§19 UPDATE_OBSERVATION."""
    return update_track(track, obs)


__all__ = [
    "Symbol", "Expansion", "Intent", "Context", "Event", "Entity",
    "Observation", "Track", "Operator", "ExecNode", "ExecEdge", "ExecGraph",
    "Status", "SYMBOL_TABLE", "OPERATOR_TABLE", "OPERATOR_BACKENDS",
    "register_symbol", "register_operator", "resolve_symbols",
    "compile_intent", "ingest_intent", "run", "update_observation",
    "update_track", "compress", "find_symbol_for",
    "check_preconditions", "invariants", "ExecTrace",
]
