"""Denotation of UDAG — undirected acyclic graph.

An undirected graph is a set of nodes and a set of unordered pairs of
nodes. It is acyclic iff it is a forest: for every edge, adding it must
not connect two nodes already connected by other edges.

denotes_udag(g) returns a Verdict: ok, reason, nodes, edges.
It does not raise. It names the reason.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Verdict:
    ok: bool
    reason: str
    nodes: int = 0
    edges: int = 0


def denotes_udag(graph) -> Verdict:
    try:
        nodes, edges = graph
    except (TypeError, ValueError):
        return Verdict(False, "graph is not a (nodes, edges) pair")

    nodes = set(nodes)
    edge_list = list(edges)
    seen: set[frozenset] = set()
    for e in edge_list:
        if not isinstance(e, (tuple, frozenset)) or len(e) != 2:
            return Verdict(False, f"edge is not an unordered pair: {e!r}")
        u, v = tuple(e)
        if u not in nodes or v not in nodes:
            return Verdict(False, f"edge references unknown node: {u!r} or {v!r}")
        if u == v:
            return Verdict(False, f"self loop: {u!r}")
        key = frozenset((u, v))
        if key in seen:
            return Verdict(False, f"duplicate edge: {tuple(e)!r}")
        seen.add(key)

    # Union-find over nodes; every edge must merge two distinct components.
    parent = {n: n for n in nodes}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for e in edge_list:
        u, v = tuple(e)
        ru, rv = find(u), find(v)
        if ru == rv:
            return Verdict(False, f"cycle through {u!r} and {v!r}",
                           len(nodes), len(edge_list))
        parent[ru] = rv

    return Verdict(True,
                   f"undirected, acyclic, {len(nodes)} nodes, {len(edge_list)} edges",
                   len(nodes), len(edge_list))


if __name__ == "__main__":
    import sys
    cases = [
        (({1,2,3}, {(1,2),(2,3)}), True),
        (({1,2,3}, {(1,2),(2,3),(3,1)}), False),
        (({1,2,3}, {(1,2),(1,3)}), True),          # star: acyclic
        (({1}, set()), True),
        (({1,2}, {(1,1)}), False),
        (({1,2}, {(1,3)}), False),
        (({1,2}, {(1,2),(2,1)}), False),            # duplicate undirected
        (("x",), False),
    ]
    fail = 0
    for g, expected in cases:
        v = denotes_udag(g)
        ok = v.ok == expected
        print(f"  {'ok' if ok else 'FAIL':4}  {v.reason}")
        if not ok:
            fail += 1
    print(f"\n{len(cases)-fail} ok, {fail} fail")
    sys.exit(0 if fail == 0 else 1)
