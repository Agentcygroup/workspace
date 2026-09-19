"""Enumerate every surface endpoint the repo exposes.

Sources:
  - web/backend.py ROUTES dict (HTTP paths)
  - cli/sovereign case arms (shell commands)
  - every *__main__* in substitutes (self-test surface)
"""
from __future__ import annotations
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "infra" / "endpoints.json"


def http_endpoints() -> list[dict]:
    src = (ROOT / "web" / "backend.py").read_text()
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if (isinstance(k, ast.Tuple) and len(k.elts) == 2
                        and all(isinstance(e, ast.Constant) for e in k.elts)):
                    method, path = k.elts[0].value, k.elts[1].value
                    out.append({"kind": "http", "method": method, "path": path,
                                "port": 8765})
    return out


def cli_endpoints() -> list[dict]:
    src = (ROOT / "cli" / "sovereign").read_text()
    out = []
    for m in re.finditer(r"^\s{2}([a-z]+)\)", src, flags=re.MULTILINE):
        out.append({"kind": "cli", "command": m.group(1)})
    return out


def selftest_endpoints() -> list[dict]:
    out = []
    for p in sorted((ROOT / "infra").glob("*.py")) + \
             sorted((ROOT / "cms").glob("*.py")) + \
             sorted((ROOT / "vec").glob("*.py")) + \
             sorted((ROOT / "pin").glob("*.py")) + \
             sorted((ROOT / "search").glob("*.py")):
        text = p.read_text()
        if '__name__ == "__main__"' in text or "__name__ == '__main__'" in text:
            out.append({"kind": "selftest", "file": str(p.relative_to(ROOT))})
    return out


def main() -> int:
    data = {
        "http": http_endpoints(),
        "cli": cli_endpoints(),
        "selftest": selftest_endpoints(),
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print(f"http:     {len(data['http'])}")
    print(f"cli:      {len(data['cli'])}")
    print(f"selftest: {len(data['selftest'])}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
