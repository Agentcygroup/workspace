from pathlib import Path

LAYOUT = [
    "mesh/specs",
    "mesh/engines",
    "mesh/tests",
    "mesh/emitted",
    "mesh/build",
]

def build(ctx):
    root = Path(ctx["root"])
    written = []
    for d in LAYOUT:
        p = root / d
        p.mkdir(parents=True, exist_ok=True)
        written.append(str(p))
    return {"stage": "scaffold", "written": written}
