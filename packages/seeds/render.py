"""CLI: python packages/seeds/render.py [--all] [--diff DIR] [<query>]

  --all            render every default query to docs/mermaids/
  --diff DIR       compare against a baseline directory
  <query>          render one query to docs/mermaids/<query>.mmd
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from seeds import seed_all, render_all, diff_mermaid, to_mermaid

ROOT = HERE.parent.parent
OUT = ROOT / "docs" / "mermaids"


def main(argv=None):
    argv = argv or sys.argv[1:]
    if "--all" in argv or not argv:
        written = render_all(ROOT, OUT)
        print(f"rendered {len(written)} files to {OUT}")
        for name, text in sorted(written.items()):
            print(f"  {name:16} {len(text.splitlines())} lines")
        return 0
    if "--diff" in argv:
        i = argv.index("--diff")
        baseline = Path(argv[i + 1])
        for q in ["requirement", "gate", "decision", "security", "quality"]:
            d = diff_mermaid(ROOT, q, baseline)
            print(json.dumps(d, indent=2))
        return 0
    query = argv[0]
    g = seed_all(ROOT)
    from seeds import dendritic_field, to_mermaid_field
    field = dendritic_field(g, query, hops=3)
    if not field:
        print(f"no nodes match: {query!r}")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    text = to_mermaid_field(g, field)
    (OUT / f"{query}.mmd").write_text(text)
    print(f"wrote {OUT / f'{query}.mmd'}  ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
