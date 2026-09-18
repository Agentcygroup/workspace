"""Extend the seed graph to cover things seeder.py misses.

Adds: UCI specs, model registry, expanded corpus, counterexample,
factory report, every git commit, per-artifact hash roots.
"""
from __future__ import annotations
import ast
import hashlib
import json
import subprocess
from pathlib import Path
from .schema import Graph, Node, Edge


def _nid(kind: str, name: str) -> str:
    return f"{kind}:{name}"


def _file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def _git_all(root: Path) -> list[dict]:
    r = subprocess.run(
        ["git", "log", "--pretty=format:%H|%ai|%an|%s"],
        cwd=root, capture_output=True, text=True, timeout=15,
    )
    out = []
    if r.returncode != 0:
        return out
    for line in r.stdout.splitlines():
        parts = line.split("|", 3)
        if len(parts) == 4:
            out.append({"hash": parts[0], "date": parts[1],
                        "author": parts[2], "subject": parts[3]})
    return out


def _artifact_root_nodes(root: Path, g: Graph) -> None:
    """One standards_artifact node per file in standards/, with hash and size."""
    std = root / "standards"
    if not std.exists():
        return
    for p in sorted(std.glob("*.json")):
        if p.name == "INDEX.json":
            continue
        aid = _nid("standards_artifact", p.stem)
        g.add_node(Node(aid, "standards_artifact", p.stem, {
            "hash": _file_hash(p),
            "size": p.stat().st_size,
            "path": str(p.relative_to(root)),
        }))
        g.add_edge(Edge("artifact:INDEX", aid, "lists"))
        g.add_edge(Edge(aid, _nid("artifact", p.stem), "materializes"))


def _decision_root_nodes(root: Path, g: Graph) -> None:
    dec = root / "decisions"
    if not dec.exists():
        return
    for p in sorted(dec.glob("*.json")):
        did = _nid("decision_file", p.stem)
        raw = json.loads(p.read_text())
        g.add_node(Node(did, "decision_file", p.stem, {
            "hash": _file_hash(p),
            "status": raw.get("status", "unknown"),
            "declared_by": raw.get("declared_by", "unset"),
        }))


def _uci_specs(root: Path, g: Graph) -> None:
    d = root / "mesh" / "specs_uci"
    if not d.exists():
        return
    for p in sorted(d.glob("*.json")):
        raw = json.loads(p.read_text())
        sid = _nid("uci_spec", raw.get("kind_id", p.stem))
        g.add_node(Node(sid, "uci_spec", raw.get("kind_id", p.stem), {
            "components": len(raw.get("components", [])),
            "interfaces": len(raw.get("interfaces", [])),
            "model": raw.get("model"),
        }))
        if raw.get("model"):
            mid = _nid("model", raw["model"])
            g.add_node(Node(mid, "model", raw["model"]))
            g.add_edge(Edge(sid, mid, "binds"))


def _expanded_and_counterexample(root: Path, g: Graph) -> None:
    for sub, kind in [("mesh/specs_expanded", "expanded_spec"),
                      ("mesh/specs_counterexample", "counterexample_spec")]:
        d = root / sub
        if not d.exists():
            continue
        for p in sorted(d.glob("*.json")):
            raw = json.loads(p.read_text())
            sid = _nid(kind, raw.get("kind_id", p.stem))
            g.add_node(Node(sid, kind, raw.get("kind_id", p.stem), {
                "components": len(raw.get("components", [])),
                "interfaces": len(raw.get("interfaces", [])),
                "gaps": len(raw.get("gaps", [])),
            }))


def _model_registry(root: Path, g: Graph) -> None:
    models_dir = root / "packages" / "buildability" / "src" / "buildability" / "models"
    if not models_dir.exists():
        return
    for p in sorted(models_dir.glob("*.py")):
        if p.name == "__init__.py":
            continue
        mid = _nid("model", p.stem)
        g.add_node(Node(mid, "model", p.stem, {
            "path": str(p.relative_to(root)),
            "size": p.stat().st_size,
        }))


def _factory_report(root: Path, g: Graph) -> None:
    rp = root / "mesh" / "report.json"
    if not rp.exists():
        return
    raw = json.loads(rp.read_text())
    rid = _nid("factory_report", "mesh")
    g.add_node(Node(rid, "factory_report", "mesh", {
        "total": raw.get("total"),
        "emitted": raw.get("emitted"),
        "skipped_invalid": raw.get("skipped_invalid"),
    }))


def _all_commits(root: Path, g: Graph) -> None:
    for c in _git_all(root):
        cid = _nid("commit", c["hash"][:12])
        g.add_node(Node(cid, "commit", c["hash"][:12], {
            "date": c["date"], "author": c["author"], "subject": c["subject"],
        }))
        g.add_edge(Edge(cid, "artifact:provenance_record", "recorded_in"))


def extend(g: Graph, root: Path) -> Graph:
    _artifact_root_nodes(root, g)
    _decision_root_nodes(root, g)
    _uci_specs(root, g)
    _expanded_and_counterexample(root, g)
    _model_registry(root, g)
    _factory_report(root, g)
    _all_commits(root, g)
    return g
