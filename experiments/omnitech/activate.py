import json, sys
from pathlib import Path
from collections import defaultdict

nodes = json.loads(Path("experiments/omnitech/nodes.json").read_text())
edges = json.loads(Path("experiments/omnitech/edges.json").read_text())

display = {n["key"]: n["display"] for n in nodes}
adj = defaultdict(list)
for e in edges:
    adj[e["source"]].append((e["target"], e["weight"]))

DECAY, THRESHOLD = 0.6, 0.15

def activate(query, hops=3):
    query = query.lower()
    if query not in display:
        return [], {}
    activation = {query: 1.0}
    frontier = {query}
    fired = {query}
    for _ in range(hops):
        new = {}
        for node in frontier:
            a = activation[node]
            for target, w in adj[node]:
                new[target] = new.get(target, 0.0) + a * DECAY * min(w, 3) / 3.0
        for target, amt in new.items():
            activation[target] = activation.get(target, 0.0) + amt
            if activation[target] >= THRESHOLD:
                fired.add(target)
        frontier = set(new.keys())
        if not frontier:
            break
    return sorted(fired, key=lambda t: -activation.get(t, 0)), activation

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "OmniTech"
    field, act = activate(q)
    print(f"query: {q!r}")
    print(f"dendritic field: {len(field)} nodes")
    for t in field[:40]:
        print(f"  {act[t]:.3f}  {display[t]}")
