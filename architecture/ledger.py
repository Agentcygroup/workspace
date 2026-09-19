"""Ledger of every committed Python file and the tests that import it.

For each project:
  1. find every tests directory
  2. run `pytest --collect-only -q <dir>` in it
  3. parse the collected test node IDs into (file, name) pairs
  4. parse each test file's AST and record which modules it imports
  5. map each module path to the test node IDs that import it

Writes architecture/ledger.json. Refuses to invent: a module with no
importing test gets `tests: []`.
"""
from __future__ import annotations
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent
OMINOUSCENT = Path.home() / "OMINOUSCENT"
OUT = HERE / "ledger.json"


def find_tests_dirs(root: Path) -> list[Path]:
    out = []
    for d in root.rglob("tests"):
        if d.is_dir() and ".venv" not in d.parts and ".git" not in d.parts:
            out.append(d)
    for d in root.rglob("test_*.py"):
        if ".venv" in d.parts or ".git" in d.parts:
            continue
        if d.parent not in out:
            out.append(d.parent)
    for d in root.rglob("tests_*.py"):
        if ".venv" in d.parts or ".git" in d.parts:
            continue
        if d.parent not in out:
            out.append(d.parent)
    return out


def collect_node_ids(root: Path, tests_dir: Path) -> list[str]:
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", str(tests_dir)],
            capture_output=True, text=True, timeout=60, cwd=root,
        )
    except Exception:
        return []
    ids = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if "::" in line and not line.startswith("="):
            ids.append(line)
    return ids


def imports_of(test_file: Path, module_roots: dict[str, Path]) -> set[Path]:
    """Return the set of module files this test file imports."""
    try:
        tree = ast.parse(test_file.read_text(errors="ignore"))
    except SyntaxError:
        return set()
    found: set[Path] = set()
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        for n in names:
            top = n.split(".")[0]
            if top in module_roots:
                found.add(module_roots[top])
    return found


def module_file(root: Path, top: str) -> Path | None:
    for base in (root, root / "packages"):
        for cand in (base / top, base / top / "__init__.py"):
            if cand.is_file() and cand.suffix == ".py":
                return cand
            pkg = base / "packages" / top / "src" / top
            if pkg.is_dir():
                return pkg / "__init__.py"
        pkg = root / "packages" / top / "src" / top
        if pkg.is_dir():
            return pkg / "__init__.py"
    for p in root.rglob(f"{top}.py"):
        if ".venv" in p.parts or ".git" in p.parts:
            continue
        return p
    for p in root.rglob(f"{top}/__init__.py"):
        if ".venv" in p.parts or ".git" in p.parts:
            continue
        return p
    return None


def scan(root: Path, label: str) -> dict:
    tests_dirs = find_tests_dirs(root)
    node_ids_by_dir: dict[Path, list[str]] = {}
    for d in tests_dirs:
        node_ids_by_dir[d] = collect_node_ids(root, d)

    # Build a map of top-level name -> module file.
    module_roots: dict[str, Path] = {}
    for py in root.rglob("*.py"):
        if ".venv" in py.parts or ".git" in py.parts:
            continue
        if py.name.startswith(("test_", "tests_")):
            continue
        top = py.stem if py.name != "__init__.py" else py.parent.name
        module_roots.setdefault(top, py)

    # Map each test file to the modules it imports.
    tests_to_modules: dict[Path, set[Path]] = {}
    for d in tests_dirs:
        for tf in list(d.glob("test_*.py")) + list(d.glob("tests_*.py")):
            tests_to_modules[tf] = imports_of(tf, module_roots)
    for tf in list(root.rglob("test_*.py")) + list(root.rglob("tests_*.py")):
        if ".venv" in tf.parts or ".git" in tf.parts:
            continue
        tests_to_modules.setdefault(tf, imports_of(tf, module_roots))

    # For each module, gather the tests that import it and their node ids.
    modules: list[dict] = []
    for py in sorted(root.rglob("*.py")):
        if ".venv" in py.parts or ".git" in py.parts:
            continue
        if py.name.startswith(("test_", "tests_")):
            continue
        importers = []
        for tf, mods in tests_to_modules.items():
            if py in mods:
                ids = [
                    nid for nid in sum(node_ids_by_dir.values(), [])
                    if nid.split("::")[0].endswith(tf.name)
                ]
                importers.append({
                    "tests_file": str(tf.relative_to(root)),
                    "node_ids": ids,
                })
        modules.append({
            "project": label,
            "module": str(py.relative_to(root)),
            "tests": importers,
        })
    return {
        "project": label,
        "root": str(root),
        "tests_dirs": [str(d.relative_to(root)) for d in tests_dirs],
        "node_ids_collected": sum(len(v) for v in node_ids_by_dir.values()),
        "modules": modules,
    }


def main() -> int:
    ws = scan(WORKSPACE, "workspace")
    oc = scan(OMINOUSCENT, "ominouscent") if OMINOUSCENT.exists() else {"modules": [], "node_ids_collected": 0}
    total_modules = len(ws["modules"]) + len(oc["modules"])
    with_tests = sum(1 for m in ws["modules"] + oc["modules"] if m["tests"])
    OUT.write_text(json.dumps({
        "workspace": ws,
        "ominouscent": oc,
        "total_modules": total_modules,
        "with_tests": with_tests,
    }, indent=2) + "\n")
    print(f"workspace modules  : {len(ws['modules'])}")
    print(f"workspace node ids : {ws['node_ids_collected']}")
    print(f"ominouscent modules: {len(oc['modules'])}")
    print(f"ominouscent ids    : {oc.get('node_ids_collected', 0)}")
    print(f"total modules      : {total_modules}")
    print(f"with_tests         : {with_tests}")
    print(f"wrote {OUT.relative_to(WORKSPACE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
