"""Graph schema: typed nodes and edges over standards artifacts."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Node:
    id: str
    kind: str           # artifact | requirement | test | gate | decision | control | characteristic | role
    label: str
    meta: dict = field(default_factory=dict, hash=False)


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    kind: str           # verifies | depends_on | maps_to | declares | tests | refuses
    weight: float = 1.0


@dataclass
class Graph:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)

    def add_node(self, n: Node) -> None:
        self.nodes[n.id] = n

    def add_edge(self, e: Edge) -> None:
        self.edges.append(e)

    def out_edges(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges if e.src == node_id]

    def in_edges(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges if e.dst == node_id]

    def neighbors(self, node_id: str) -> set[str]:
        out = {e.dst for e in self.out_edges(node_id)}
        inn = {e.src for e in self.in_edges(node_id)}
        return out | inn

    def stats(self) -> dict:
        from collections import Counter
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "node_kinds": dict(Counter(n.kind for n in self.nodes.values())),
            "edge_kinds": dict(Counter(e.kind for e in self.edges)),
        }
