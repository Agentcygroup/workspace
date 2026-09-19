"""Denotation of DAG — a directed acyclic graph.

A graph is a pair (nodes, edges) where nodes is a set of hashable
values and edges is a set of ordered pairs (u, v) with u, v in nodes.

denotes_dag(g) returns True iff g is directed and acyclic, False
otherwise. It does not raise. It names the reason in a Verdict.

    >>> denotes_dag(({1,2,3}, {(1,2),(2,3)}))
    Verdict(ok=True, reason='directed, acyclic, 3 nodes, 2 edges')
    >>> denotes_dag(({1,2,3}, {(1,2),(2,3),(3,1)}))
    Verdict(ok=False, reason='cycle: 1 -> 2 -> 3 -> 1')
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import chain


@dataclass(frozen=True)
class Verdict:
    ok: bool
    reason: str
    nodes: int = 0
    edges: int = 0


def denotes_dag(graph) -> Verdict:
    try:
        nodes, edges = graph
    except (TypeError, ValueError):
        return Verdict(False, "graph is not a (nodes, edges) pair")

    nodes = set(nodes)
    edge_list = list(edges)
    for e in edge_list:
        if not isinstance(e, tuple) or len(e) != 2:
            return Verdict(False, f"edge is not an ordered pair: {e!r}")
        u, v = e
        if u not in nodes:
            return Verdict(False, f"edge references unknown node: {u!r}")
        if v not in nodes:
            return Verdict(False, f"edge references unknown node: {v!r}")

    adj: dict = {n: [] for n in nodes}
    for u, v in edge_list:
        adj[u].append(v)

    # Detect cycles by depth-first search. A node reachable from itself
    # through a path of length >= 1 is a cycle.
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}

    def visit(start):
        stack = [(start, iter(adj[start]))]
        color[start] = GRAY
        while stack:
            node, it = stack[-1]
            advanced = False
            for nxt in it:
                if color[nxt] == GRAY:
                    return f"cycle through {nxt!r}"
                if color[nxt] == WHITE:
                    color[nxt] = GRAY
                    stack.append((nxt, iter(adj[nxt])))
                    advanced = True
                    break
            if not advanced:
                color[node] = BLACK
                stack.pop()
        return None

    for n in nodes:
        if color[n] == WHITE:
            cyc = visit(n)
            if cyc:
                return Verdict(False, cyc, len(nodes), len(edge_list))

    return Verdict(True,
                   f"directed, acyclic, {len(nodes)} nodes, {len(edge_list)} edges",
                   len(nodes), len(edge_list))


if __name__ == "__main__":
    import sys
    cases = [
        (({1,2,3}, {(1,2),(2,3)}), True),
        (({1,2,3}, {(1,2),(2,3),(3,1)}), False),
        (({1}, set()), True),
        (({1,2}, {(1,1)}), False),
        (({1,2}, {(1,3)}), False),
        (("not a graph",), False),
    ]
    fail = 0
    for g, expected in cases:
        v = denotes_dag(g)
        ok = v.ok == expected
        print(f"  {'ok' if ok else 'FAIL':4}  {v.reason}")
        if not ok:
            fail += 1
    print(f"\n{len(cases) - fail} ok, {fail} fail")
    sys.exit(0 if fail == 0 else 1)
