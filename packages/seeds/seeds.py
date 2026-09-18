"""CLI: python packages/seeds/seeds.py [<query>] [--full] [--stats]

  no args       print graph stats and the full mermaid
  <query>       print the dendritic mermaid for the query term
  --stats       print only stats
  --full        print the whole graph mermaid
  --write DIR   write the mermaid to DIR/<query>.mmd
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))

from seeds import seed_all, to_mermaid, to_mermaid_field, dendritic_field


def main(argv=None):
    argv = argv or sys.argv[1:]
    root = HERE.parent.parent
    graph = seed_all(root)

    # Parse args, consuming --write DIR so DIR isn't treated as query text.
    args = []
    flags = set()
    write_dir = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--write":
            if i + 1 >= len(argv):
                print("--write needs a directory", file=sys.stderr)
                return 2
            write_dir = Path(argv[i + 1])
            i += 2
            continue
        if a.startswith("--"):
            flags.add(a)
            i += 1
            continue
        args.append(a)
        i += 1

    if not args or "--full" in flags:
        stats = graph.stats()
        print(f"nodes: {stats['nodes']}")
        print(f"edges: {stats['edges']}")
        print(f"node kinds: {stats['node_kinds']}")
        print(f"edge kinds: {stats['edge_kinds']}")
        print()
        if "--stats" not in flags:
            print(to_mermaid(graph))
        if write_dir:
            write_dir.mkdir(parents=True, exist_ok=True)
            (write_dir / "full.mmd").write_text(to_mermaid(graph))
            print(f"\nwrote {write_dir / 'full.mmd'}")
        return 0

    query = " ".join(args)
    field = dendritic_field(graph, query, hops=3)
    if not field:
        print(f"no nodes match query: {query!r}")
        return 1
    stats = graph.stats()
    print(f"query: {query!r}")
    print(f"field: {len(field)} / {stats['nodes']} nodes")
    print()
    text = to_mermaid_field(graph, field)
    print(text)
    if write_dir:
        write_dir.mkdir(parents=True, exist_ok=True)
        safe = query.replace(" ", "_").replace("/", "_")
        (write_dir / f"{safe}.mmd").write_text(text)
        print(f"\nwrote {write_dir / f'{safe}.mmd'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
