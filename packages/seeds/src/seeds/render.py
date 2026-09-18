"""Render all query mermaids to docs/mermaids/ in one call."""
from __future__ import annotations
from pathlib import Path
from .seeder import seed_all
from .mermaid import to_mermaid, to_mermaid_field
from .query import dendritic_field


DEFAULT_QUERIES = [
    "requirement", "gate", "decision", "security", "quality",
    "framework", "characteristic", "control", "adversary",
    "model", "spec", "commit", "test", "artifact",
]


def render_all(root: Path, out_dir: Path,
               queries: list[str] | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    g = seed_all(root)
    queries = queries or DEFAULT_QUERIES
    written = {"full": to_mermaid(g)}
    (out_dir / "full.mmd").write_text(written["full"])
    for q in queries:
        field = dendritic_field(g, q, hops=3)
        if not field:
            continue
        text = to_mermaid_field(g, field)
        (out_dir / f"{q}.mmd").write_text(text)
        written[q] = text
    return written


def diff_mermaid(root: Path, query: str, baseline_dir: Path) -> dict:
    """Compare a freshly rendered mermaid to a baseline file.

    Returns lines added and removed. The review surface for a decision
    change: run this and see the edge delta.
    """
    g = seed_all(root)
    field = dendritic_field(g, query, hops=3)
    current = to_mermaid_field(g, field)
    baseline_path = baseline_dir / f"{query}.mmd"
    if not baseline_path.exists():
        return {"query": query, "status": "no-baseline",
                "current_lines": current.count("\n")}
    baseline = baseline_path.read_text()
    cur = set(current.splitlines())
    base = set(baseline.splitlines())
    return {
        "query": query,
        "status": "diff",
        "added": sorted(cur - base),
        "removed": sorted(base - cur),
        "current_lines": current.count("\n"),
        "baseline_lines": baseline.count("\n"),
    }
