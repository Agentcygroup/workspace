import json, re
from pathlib import Path
from collections import defaultdict, Counter

raw = Path("experiments/glossary/raw.txt").read_text()
lines = raw.split("\n")

entries = {}
current_term = None
current_body = []

def flush():
    if current_term and current_body:
        entries[current_term] = " ".join(current_body).strip()

for line in lines:
    s = line.strip()
    if not s:
        continue
    words = s.split()
    is_short = len(s) < 90
    is_heading = is_short and len(words) <= 8 and not s.endswith(".")
    if is_heading:
        flush()
        current_term = s
        current_body = []
    elif current_term:
        current_body.append(s)

flush()

term_names = list(entries.keys())
edges = []
in_deg = Counter()
out_deg = Counter()

for term, body in entries.items():
    body_lower = body.lower()
    for other in term_names:
        if other == term:
            continue
        hits = len(re.findall(r"\b" + re.escape(other.lower()) + r"\b", body_lower))
        if hits > 0:
            edges.append({"source": term, "target": other, "weight": hits})
            out_deg[term] += 1
            in_deg[other] += 1

Path("experiments/glossary/nodes.json").write_text(
    json.dumps([{"term": t, "definition": d} for t, d in entries.items()], indent=2))
Path("experiments/glossary/edges.json").write_text(json.dumps(edges, indent=2))
Path("experiments/glossary/stats.json").write_text(json.dumps({
    "nodes": len(entries),
    "edges": len(edges),
    "top_in_degree": in_deg.most_common(20),
}, indent=2))

print(f"nodes: {len(entries)}")
print(f"edges: {len(edges)}")
print("top 20 hubs by in-degree:")
for term, deg in in_deg.most_common(20):
    print(f"  {deg:5}  {term}")
