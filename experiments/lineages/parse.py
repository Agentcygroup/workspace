import json, re
from pathlib import Path
from collections import defaultdict, Counter

raw = Path("experiments/lineages/raw.txt").read_text()
lines = [l.strip() for l in raw.split("\n") if l.strip()]

current_lineage = None
current_person = None
records = []

for line in lines:
    if line == "SECTION":
        current_lineage = None
        current_person = None
        continue
    if re.match(r"^(I|II|III|IV|V|VI|VII|VIII|IX)\.\s", line):
        current_lineage = line
        current_person = None
        continue
    if current_lineage is None:
        continue
    if current_person is None:
        current_person = line
    else:
        records.append({"lineage": current_lineage, "person": current_person, "primitive": line})
        current_person = None

lineage_members = defaultdict(list)
person_lineages = defaultdict(list)
for r in records:
    for p in re.split(r"\s*/\s*", r["person"]):
        p = p.strip()
        if p:
            lineage_members[r["lineage"]].append(p)
            person_lineages[p].append(r["lineage"])

colineage = []
for lineage, members in lineage_members.items():
    unique = sorted(set(members))
    for i, a in enumerate(unique):
        for b in unique[i+1:]:
            colineage.append({"source": a, "target": b, "lineage": lineage})

lineage_size = {l: len(set(m)) for l, m in lineage_members.items()}
multi = {p: ls for p, ls in person_lineages.items() if len(set(ls)) > 1}
prim_counts = Counter(r["primitive"] for r in records)

Path("experiments/lineages/nodes.json").write_text(json.dumps(records, indent=2))
Path("experiments/lineages/attributions.json").write_text(json.dumps([
    {"source": r["person"], "target": r["primitive"], "lineage": r["lineage"]} for r in records
], indent=2))
Path("experiments/lineages/colineage.json").write_text(json.dumps(colineage, indent=2))
Path("experiments/lineages/lineages.json").write_text(json.dumps(
    {l: sorted(set(m)) for l, m in lineage_members.items()}, indent=2))
Path("experiments/lineages/stats.json").write_text(json.dumps({
    "records": len(records),
    "lineages": len(lineage_members),
    "unique_people": len(person_lineages),
    "lineage_sizes": lineage_size,
    "multi_lineage_people": multi,
    "recurring_primitives": [p for p, c in prim_counts.items() if c > 1],
}, indent=2))

print(f"records: {len(records)}")
print(f"lineages: {len(lineage_members)}")
print(f"unique people: {len(person_lineages)}")
print("lineage sizes:")
for l, n in lineage_size.items():
    print(f"  {n:3}  {l}")
print("people in >1 lineage:")
for p, ls in multi.items():
    print(f"  {p}: {len(set(ls))} lineages")
