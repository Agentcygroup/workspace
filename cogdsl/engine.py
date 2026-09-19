"""§12: execution engine.

Runs nodes in order. A node whose preconditions fail is marked FAILED
and the executor refuses to proceed past it. The refusal reason is
written into the node's outputs so a trace can name it.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from .schema import (
    Context, ExecGraph, ExecNode, Status,
    OPERATOR_TABLE, OPERATOR_BACKENDS,
)


@dataclass
class ExecTrace:
    executed: list[str] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


def check_preconditions(node: ExecNode, ctx: Context) -> tuple[bool, str]:
    op = OPERATOR_TABLE.get(node.operator)
    if op is None:
        return False, f"operator not registered: {node.operator!r}"
    for k, required in op.preconditions.items():
        value = node.inputs.get(k, ctx.environment.get(k))
        if value is None:
            return False, f"precondition missing: {k!r}"
        if value != required:
            return False, f"precondition mismatch: {k!r} = {value!r}, want {required!r}"
    return True, ""


def run_operator(op_id: str, inputs: dict, ctx: Context) -> dict:
    backend = OPERATOR_BACKENDS.get(op_id)
    if backend is None:
        return {"_backend": "missing", "_op": op_id}
    return backend(inputs, ctx)


def execute(graph: ExecGraph, ctx: Context) -> ExecTrace:
    """§12 EXECUTE. Returns the trace; the graph is mutated in place."""
    trace = ExecTrace()
    for node in graph.nodes:
        ok, reason = check_preconditions(node, ctx)
        if not ok:
            node.status = Status.FAILED
            node.outputs["_refused"] = reason
            trace.failed.append((node.id, reason))
            continue
        node.status = Status.RUNNING
        result = run_operator(node.operator, node.inputs, ctx)
        node.outputs.update(result)
        node.status = Status.DONE
        trace.executed.append(node.id)
        ctx.record("node_done", {"node": node.id, "op": node.operator,
                                 "outputs": {k: str(v) for k, v in result.items()}})
    return trace
