"""Collect everything the repo actually contains. Nothing invented."""
from __future__ import annotations
import ast
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Evidence:
    root: Path
    commits: list = field(default_factory=list)
    tests: list = field(default_factory=list)
    modules: list = field(default_factory=list)
    specs: list = field(default_factory=list)
    outcomes: list = field(default_factory=list)
    git_dirty: bool = False


def _git(root, *args):
    try:
        r = subprocess.run(["git", *args], cwd=root,
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def collect(root: Path) -> Evidence:
    ev = Evidence(root=root)

    log = _git(root, "log", "--pretty=format:%H|%ai|%an|%s", "-n", "500")
    for line in log.splitlines():
        parts = line.split("|", 3)
        if len(parts) == 4:
            ev.commits.append({
                "hash": parts[0], "date": parts[1],
                "author": parts[2], "subject": parts[3],
            })

    ev.git_dirty = bool(_git(root, "status", "--porcelain"))

    for test_file in (root / "packages").rglob("test_*.py"):
        try:
            tree = ast.parse(test_file.read_text())
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                doc = ast.get_docstring(node) or ""
                ev.tests.append({
                    "name": node.name,
                    "file": str(test_file.relative_to(root)),
                    "line": node.lineno,
                    "doc": doc.strip().split("\n")[0] if doc else "",
                })

    for src_file in (root / "packages").rglob("*.py"):
        if "test_" in src_file.name:
            continue
        try:
            tree = ast.parse(src_file.read_text())
        except SyntaxError:
            continue
        mod_doc = ast.get_docstring(tree) or ""
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "Gate":
                gates = []
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for t in item.targets:
                            if isinstance(t, ast.Name):
                                gates.append(t.id)
                if gates:
                    ev.modules.append({
                        "file": str(src_file.relative_to(root)),
                        "module": src_file.stem,
                        "doc": mod_doc.strip().split("\n")[0] if mod_doc else "",
                        "gates": gates,
                    })
            if isinstance(node, ast.FunctionDef) and node.name.startswith("_g"):
                ev.modules.append({
                    "file": str(src_file.relative_to(root)),
                    "function": node.name,
                    "doc": (ast.get_docstring(node) or "").strip().split("\n")[0],
                })

    for spec_dir in ["mesh/specs_uci", "mesh/specs_expanded",
                     "mesh/specs_counterexample", "mesh/specs"]:
        d = root / spec_dir
        if d.exists():
            for p in d.glob("*.json"):
                try:
                    raw = json.loads(p.read_text())
                    ev.specs.append({
                        "path": str(p.relative_to(root)),
                        "kind_id": raw.get("kind_id", p.stem),
                        "components": len(raw.get("components", [])),
                        "interfaces": len(raw.get("interfaces", [])),
                        "model": raw.get("model"),
                    })
                except Exception:
                    pass

    for p in (root / "experiments").rglob("*outcome*.json"):
        try:
            ev.outcomes.append({
                "path": str(p.relative_to(root)),
                "record": json.loads(p.read_text()),
            })
        except Exception:
            pass

    return ev
