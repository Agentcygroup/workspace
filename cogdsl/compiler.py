"""§10-§11: graph building and auto-link.

Auto-link is the schema's default policy: chain nodes in the order
they were flattened. §20 HOOK GRAPH_OPTIMIZER may replace this.
"""
from __future__ import annotations
import uuid
from .schema import (
    Intent, Expansion, ExecGraph, ExecNode, ExecEdge, Status,
    OPERATOR_TABLE,
)
from . import symbols as sy


GRAPH_OPTIMIZER = None   # §20 hook; callable(graph) -> graph


def _apply_constraints(ops: list[str], constraints: dict) -> list[str]:
    """Constraints filter operators whose registered preconditions conflict."""
    if not constraints:
        return ops
    out = []
    for op_id in ops:
        op = OPERATOR_TABLE.get(op_id)
        if op is None:
            out.append(op_id)
            continue
        conflict = any(
            op.preconditions.get(k) not in (None, v)
            for k, v in constraints.items()
        )
        if not conflict:
            out.append(op_id)
    return out


def auto_link(nodes: list[ExecNode]) -> list[ExecEdge]:
    """§11 AUTO_LINK: linear chain in node order."""
    edges: list[ExecEdge] = []
    for i in range(len(nodes) - 1):
        edges.append(ExecEdge(from_=nodes[i].id, to=nodes[i + 1].id))
    return edges


def build_graph(operators: list[str]) -> ExecGraph:
    """§10 BUILD_GRAPH."""
    nodes = [
        ExecNode(id=str(uuid.uuid4()), operator=op, status=Status.PENDING)
        for op in operators
    ]
    edges = auto_link(nodes)
    return ExecGraph(nodes=nodes, edges=edges)


def bind_defaults(graph: ExecGraph, defaults: dict) -> ExecGraph:
    """§8 BIND_DEFAULTS: every node gets the merged defaults as inputs."""
    for node in graph.nodes:
        node.inputs.update(defaults)
    return graph


def compile_intent(intent: Intent) -> ExecGraph:
    """§8 COMPILE pipeline, straight through."""
    syms = sy.resolve_symbols(intent.symbols)
    ops = sy.flatten_operators(syms)
    constraints = sy.merge_constraints(syms)
    defaults = sy.merge_defaults(syms)
    constrained = _apply_constraints(ops, constraints)
    graph = build_graph(constrained)
    graph = bind_defaults(graph, defaults)
    if GRAPH_OPTIMIZER is not None:
        graph = GRAPH_OPTIMIZER(graph)
    return graph
