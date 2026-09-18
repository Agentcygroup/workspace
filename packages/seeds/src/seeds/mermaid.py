"""Render a Graph or a dendritic field as Mermaid."""
from __future__ import annotations
from .schema import Graph

KIND_SHAPES = {
    "artifact":       ("[[", "]]"),   # stadium
    "requirement":    ("((", "))"),   # circle
    "test":           ("[", "]"),     # rectangle
    "gate":           ("{{", "}}"),   # hexagon
    "decision":       (">", "]"),     # asymmetric
    "control":        ("[", "]"),
    "framework":      ("(", ")"),     # rounded
    "characteristic": ("(", ")"),
    "threshold":      ("[", "]"),
    "role":           ("(", ")"),
    "cadence":        ("[", "]"),
    "adversary":      ("[/", "/]"),   # parallelogram
    "commit":         (">", "]"),
}

EDGE_STYLES = {
    "generated":  "-->",
    "contains":   "-->",
    "covers":     "==>",
    "verifies":   "-->",
    "traces_to":  "-->",
    "tested_by":  "-->",
    "maps_to":    "==>",
    "considers":  "-.->",
    "declares":   "-->",
    "bounded_by": "-->",
    "assigns":    "-->",
    "unlocks":    "==>",
    "recorded_in": "-.->",
}


def _shape(kind: str) -> tuple[str, str]:
    return KIND_SHAPES.get(kind, ("[", "]"))


def _safe(node_id: str) -> str:
    return node_id.replace(":", "_").replace("-", "_").replace(".", "_")


def _label(n) -> str:
    return n.label.replace('"', "'")


def to_mermaid(graph: Graph, direction: str = "TD") -> str:
    lines = [f"graph {direction}"]
    for node_id, node in sorted(graph.nodes.items()):
        open_s, close_s = _shape(node.kind)
        lines.append(f'  {_safe(node_id)}{open_s}"{_label(node)}"{close_s}')
    for e in graph.edges:
        arrow = EDGE_STYLES.get(e.kind, "-->")
        lines.append(f"  {_safe(e.src)} {arrow}|{e.kind}| {_safe(e.dst)}")
    return "\n".join(lines)


def to_mermaid_field(graph: Graph, field_nodes: set[str], direction: str = "TD") -> str:
    """Render only the subgraph induced by field_nodes."""
    lines = [f"graph {direction}"]
    for node_id in sorted(field_nodes):
        node = graph.nodes.get(node_id)
        if node is None:
            continue
        open_s, close_s = _shape(node.kind)
        lines.append(f'  {_safe(node_id)}{open_s}"{_label(node)}"{close_s}')
    for e in graph.edges:
        if e.src in field_nodes and e.dst in field_nodes:
            arrow = EDGE_STYLES.get(e.kind, "-->")
            lines.append(f"  {_safe(e.src)} {arrow}|{e.kind}| {_safe(e.dst)}")
    return "\n".join(lines)
