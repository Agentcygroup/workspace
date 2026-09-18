import json, sys
from pathlib import Path
from collections import defaultdict

attributions = json.loads(Path("experiments/lineages/attributions.json").read_text())
person_to_prim = defaultdict(set)
prim_to_person = defaultdict(set)
for a in attributions:
    person_to_prim[a["source"]].add(a["target"])
    prim_to_person[a["target"]].add(a["source"])

DECAY, THRESHOLD = 0.6, 0.15

def activate(query, hops=3):
    activation = {query: 1.0}
    frontier = {query}
    fired = {query}
    for _ in range(hops):
        new = {}
        for node in frontier:
            a = activation[node]
            neighbors = set()
            if node in person_to_prim:
                neighbors |= person_to_prim[node]
            if node in prim_to_person:
                neighbors |= prim_to_person[node]
            for t in neighbors:
                new[t] = new.get(t, 0.0) + a * DECAY
        for t, amt in new.items():
            activation[t] = activation.get(t, 0.0) + amt
            if activation[t] >= THRESHOLD:
                fired.add(t)
        frontier = set(new.keys())
        if not frontier:
            break
    return sorted(fired, key=lambda t: -activation.get(t, 0)), activation

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "Claude Shannon"
    field, act = activate(q)
    print(f"query: {q!r}")
    print(f"dendritic field: {len(field)} nodes")
    for t in field[:30]:
        kind = "person" if t in person_to_prim else "primitive"
        print(f"  {act[t]:.3f}  [{kind}] {t}")
