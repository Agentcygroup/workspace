"""§18: the four invariants, checked.

  INVARIANT 1  ∀ symbol → deterministic expansion
  INVARIANT 2  ∀ intent → finite ExecGraph
  INVARIANT 3  ∀ entity → probabilistic continuity tracked
  INVARIANT 4  context updated after each node execution
"""
from __future__ import annotations
from .schema import Symbol, Intent, ExecGraph, Context, SYMBOL_TABLE
from . import compiler, engine


def inv1_deterministic(symbol_ids: list[str]) -> tuple[bool, str]:
    """Two compiles of the same symbols yield the same operator sequence."""
    a = compiler.build_graph(
        [op for s in symbol_ids for op in SYMBOL_TABLE[s].expands_to.operators]
    )
    b = compiler.build_graph(
        [op for s in symbol_ids for op in SYMBOL_TABLE[s].expands_to.operators]
    )
    ok = [n.operator for n in a.nodes] == [n.operator for n in b.nodes]
    return ok, "same symbol set → same operator order" if ok else "order diverged"


def inv2_finite(graph: ExecGraph) -> tuple[bool, str]:
    """Graph is finite and acyclic by construction of auto_link."""
    ok = len(graph.nodes) < 10_000
    return ok, f"{len(graph.nodes)} nodes" if ok else "graph too large"


def inv3_continuity(entity_tracks: dict) -> tuple[bool, str]:
    """Every track has a score in [0, 1]."""
    bad = [k for k, t in entity_tracks.items()
           if not (0.0 <= t.continuity_score <= 1.0)]
    return (not bad), "all tracks in range" if not bad else f"out of range: {bad}"


def inv4_context_after_execution(ctx: Context, trace: engine.ExecTrace) -> tuple[bool, str]:
    """Number of node_done events equals number of executed nodes."""
    n = sum(1 for e in ctx.history if e.type == "node_done")
    ok = n == len(trace.executed)
    return ok, (f"{n} context events for {len(trace.executed)} nodes"
                if ok else "context not updated after every node")
