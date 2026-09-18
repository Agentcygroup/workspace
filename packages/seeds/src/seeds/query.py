"""Spreading activation over the seed graph."""
from __future__ import annotations
from .schema import Graph


DECAY = 0.6
THRESHOLD = 0.15


def dendritic_field(graph: Graph, query: str, hops: int = 3) -> set[str]:
    """Return the set of node ids activated by the query term.

    The query is matched against node labels and ids, case-insensitively.
    A query activates every node whose label contains the query string.
    Activation then spreads via edges with decay.
    """
    q = query.lower()
    seeds = [nid for nid, n in graph.nodes.items() if q in n.label.lower() or q in nid.lower()]
    if not seeds:
        return set()

    activation = {nid: 1.0 for nid in seeds}
    frontier = set(seeds)
    fired = set(seeds)

    for _ in range(hops):
        new = {}
        for nid in frontier:
            a = activation[nid]
            for nbr in graph.neighbors(nid):
                new[nbr] = new.get(nbr, 0.0) + a * DECAY
        for nid, amount in new.items():
            activation[nid] = activation.get(nid, 0.0) + amount
            if activation[nid] >= THRESHOLD:
                fired.add(nid)
        frontier = set(new.keys())
        if not frontier:
            break
    return fired
