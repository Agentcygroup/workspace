import json, sys
from pathlib import Path
from collections import defaultdict

nodes = json.loads(Path("experiments/glossary/nodes.json").read_text())
edges = json.loads(Path("experiments/glossary/edges.json").read_text())

adj = defaultdict(list)
for e in edges:
    adj[e["source"]].append((e["target"], e["weight"]))
    adj[e["target"]].append((e["source"], e["weight"]))

DECAY, THRESHOLD = 0.6, 0.15

def activate(query, hops=3):
    if query not in adj and not any(n["term"] == query for n in nodes):
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
    q = sys.argv[1] if len(sys.argv) > 1 else "machine learning"
    field, activation = activate(q)
    print(f"query: {q!r}")
    print(f"dendritic field: {len(field)} nodes")
    for t in field[:40]:
        print(f"  {activation[t]:.3f}  {t}")
