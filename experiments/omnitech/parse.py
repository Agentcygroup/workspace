import json
from pathlib import Path
from collections import defaultdict, Counter

raw = Path("experiments/omnitech/raw.txt").read_text()
lines = [l.strip() for l in raw.split("\n") if l.strip()]

display = {}
for line in lines:
    key = line.lower()
    if key not in display:
        display[key] = line

WINDOW = 5
edges = Counter()
for i, line in enumerate(lines):
    a = line.lower()
    for j in range(i + 1, min(i + WINDOW, len(lines))):
        b = lines[j].lower()
        if a == b:
            continue
        edges[(a, b)] += 1
        edges[(b, a)] += 1

in_deg = Counter()
for (a, b), w in edges.items():
    in_deg[b] += 1

Path("experiments/omnitech/nodes.json").write_text(json.dumps(
    [{"key": k, "display": v} for k, v in display.items()], indent=2))
Path("experiments/omnitech/edges.json").write_text(json.dumps(
    [{"source": a, "target": b, "weight": w} for (a, b), w in edges.items()], indent=2))
Path("experiments/omnitech/stats.json").write_text(json.dumps({
    "nodes": len(display),
    "edges": len(edges),
    "top_in_degree": in_deg.most_common(30),
}, indent=2))

print(f"nodes: {len(display)}")
print(f"edges: {len(edges)}")
print("top 30 hubs by in-degree:")
for key, deg in in_deg.most_common(30):
    print(f"  {deg:5}  {display[key]}")
