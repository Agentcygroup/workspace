from pathlib import Path

RUNNER = '''#!/usr/bin/env bash
set -uo pipefail
ROOT="${1:-$HOME/workspace}"
cd "$ROOT"
[ -d .venv ] && . .venv/bin/activate
python3 mesh/mesh.py
python3 -m pytest mesh/tests -q
'''

def build(ctx):
    root = Path(ctx["root"])
    p = root / "mesh" / "run.sh"
    p.write_text(RUNNER)
    p.chmod(0o755)
    return {"stage": "wire", "written": 1}
