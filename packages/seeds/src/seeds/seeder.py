"""Convert standards/ and decisions/ and the test suite into a graph.

Every artifact is a node. Every cross-reference in an artifact is an edge.
The result is a dendritic tree rooted at the artifacts.
"""
from __future__ import annotations
import ast
import json
from pathlib import Path
from .schema import Graph, Node, Edge
from .seed_extras import extend as _extend_extra


def _nid(kind: str, name: str) -> str:
    return f"{kind}:{name}"


def seed_all(root: Path) -> Graph:
    g = Graph()

    # Artifact root nodes.
    for p in sorted((root / "standards").glob("*.json")):
        if p.name == "INDEX.json":
            continue
        g.add_node(Node(_nid("artifact", p.stem), "artifact", p.stem))
    g.add_node(Node("artifact:INDEX", "artifact", "INDEX"))

    # INDEX -> artifact edges.
    index = json.loads((root / "standards" / "INDEX.json").read_text())
    for name in index["generated"]:
        g.add_edge(Edge("artifact:INDEX", _nid("artifact", name), "generated"))

    # requirements_specification: requirement -> gate, and requirement -> test.
    reqs = json.loads((root / "standards" / "requirements_specification.json").read_text())
    for r in reqs.get("requirements", []):
        rid = _nid("requirement", r["id"])
        g.add_node(Node(rid, "requirement", r["id"],
                        {"criterion": r["criterion"], "verified": r["verified"]}))
        gid = _nid("gate", r["gate"])
        g.add_node(Node(gid, "gate", r["gate"]))
        g.add_edge(Edge(rid, gid, "covers"))
        g.add_edge(Edge("artifact:requirements_specification", rid, "contains"))
        for tname in r["verification"]:
            tid = _nid("test", tname)
            g.add_node(Node(tid, "test", tname))
            g.add_edge(Edge(tid, rid, "verifies"))
            g.add_edge(Edge("artifact:traceability_matrix", tid, "contains"))

    # traceability_matrix: every row is a test -> requirement edge.
    tm = json.loads((root / "standards" / "traceability_matrix.json").read_text())
    for row in tm.get("rows", []):
        tid = _nid("test", row["test"])
        g.add_node(Node(tid, "test", row["test"],
                        {"file": row["file"], "line": row["line"]}))
        if row["requirement"]:
            rid = _nid("requirement", row["requirement"])
            g.add_node(Node(rid, "requirement", row["requirement"]))
            g.add_edge(Edge(tid, rid, "traces_to"))

    # gate_conformance: gate -> tests.
    gc = json.loads((root / "standards" / "gate_conformance.json").read_text())
    for gate, info in gc["gates"].items():
        gid = _nid("gate", gate)
        g.add_node(Node(gid, "gate", gate, {"defined_in": info["defined_in"]}))
        for tname in info["tests"]:
            tid = _nid("test", tname)
            g.add_node(Node(tid, "test", tname))
            g.add_edge(Edge(gid, tid, "tested_by"))

    # security_controls: controls mapped to frameworks.
    sc = json.loads((root / "standards" / "security_controls.json").read_text())
    for entry in sc.get("controls", []):
        cid = _nid("control", entry["control"])
        g.add_node(Node(cid, "control", entry["control"]))
        g.add_edge(Edge("artifact:security_controls", cid, "contains"))
        for fw in entry["frameworks"]:
            fid = _nid("framework", fw)
            g.add_node(Node(fid, "framework", fw))
            g.add_edge(Edge(cid, fid, "maps_to"))
    for adv in sc.get("adversaries", []):
        aid = _nid("adversary", adv)
        g.add_node(Node(aid, "adversary", adv))
        g.add_edge(Edge("artifact:security_controls", aid, "considers"))

    # quality_model: characteristics -> thresholds.
    qm = json.loads((root / "standards" / "quality_model.json").read_text())
    for char, desc in qm.get("characteristics", {}).items():
        cid = _nid("characteristic", char)
        g.add_node(Node(cid, "characteristic", char, {"desc": desc}))
        g.add_edge(Edge("artifact:quality_model", cid, "declares"))
        if char in qm.get("thresholds", {}):
            tid = _nid("threshold", char)
            g.add_node(Node(tid, "threshold", char, {"value": qm["thresholds"][char]}))
            g.add_edge(Edge(cid, tid, "bounded_by"))

    # sqa_plan: roles, cadence.
    sqa = json.loads((root / "standards" / "sqa_plan.json").read_text())
    for role, person in sqa.get("roles", {}).items():
        rid = _nid("role", role)
        g.add_node(Node(rid, "role", role, {"holder": person}))
        g.add_edge(Edge("artifact:sqa_plan", rid, "assigns"))
    if sqa.get("review_cadence"):
        cid = _nid("cadence", sqa["review_cadence"])
        g.add_node(Node(cid, "cadence", sqa["review_cadence"]))
        g.add_edge(Edge("artifact:sqa_plan", cid, "declares"))

    # ai_rmf_profile: decision.
    ai = json.loads((root / "standards" / "ai_rmf_profile.json").read_text())
    did = _nid("decision", "ai_rmf")
    g.add_node(Node(did, "decision", "ai_rmf",
                    {"is_ai": ai.get("is_ai_system_eu_ai_act"),
                     "tier": ai.get("risk_tier")}))
    g.add_edge(Edge("artifact:ai_rmf_profile", did, "declares"))

    # decisions/*.json -> the artifact each unlocks.
    for p in sorted((root / "decisions").glob("*.json")):
        did = _nid("decision", p.stem)
        g.add_node(Node(did, "decision", p.stem,
                        {"status": json.loads(p.read_text()).get("status", "pending")}))
        artifact = {
            "security": "security_controls",
            "ai_rmf": "ai_rmf_profile",
            "sqa": "sqa_plan",
            "quality_model": "quality_model",
        }.get(p.stem)
        if artifact:
            g.add_edge(Edge(did, _nid("artifact", artifact), "unlocks"))

    # Test functions from source, as leaf nodes.
    for tf in (root / "packages").rglob("test_*.py"):
        try:
            tree = ast.parse(tf.read_text())
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                tid = _nid("test", node.name)
                if tid not in g.nodes:
                    g.add_node(Node(tid, "test", node.name,
                                    {"file": str(tf.relative_to(root)),
                                     "line": node.lineno}))

    # Provenance commits as decision-adjacent nodes.
    prov = json.loads((root / "standards" / "provenance_record.json").read_text())
    for act in prov.get("activities", [])[-10:]:
        cid = _nid("commit", act["id"])
        g.add_node(Node(cid, "commit", act["id"], {"label": act["label"]}))
        g.add_edge(Edge(cid, "artifact:provenance_record", "recorded_in"))

    g = _extend_extra(g, root)
    return g
