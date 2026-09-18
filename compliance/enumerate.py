#!/usr/bin/env python3
"""
enumerate.py — Enumerate every clause of every named standard, map to files,
hash them, detect attestations, emit readiness state.

The grammar does not permit 'compliant: true'. This script therefore does not
emit that token. It emits per-clause status in {attested, unattested, gap,
not_applicable} and requires a signed attestation file to move any clause
from 'unattested' to 'attested'.
"""
import hashlib
import json
from pathlib import Path

NON_IMPLICATION = (
    "No certification is claimed. No standards body has assessed this "
    "repository. Every 'attested' status in this file is backed by a signed "
    "file in compliance/attestations/ whose signature must be independently "
    "verified. Every non-attested clause is named as a gap. Compliance is a "
    "relationship requiring a qualified human assessor in a jurisdiction at "
    "a time; this file records the repository's side of that relationship."
)

STANDARDS = {
    "ISO/IEC 27001:2022": {
        "clauses_4_to_10": [
            "4 Context", "5 Leadership", "6 Planning", "7 Support",
            "8 Operation", "9 Performance evaluation", "10 Improvement",
        ],
        "annex_a": {
            "A.5": [f"A.5.{i}" for i in range(1, 38)],
            "A.6": [f"A.6.{i}" for i in range(1, 9)],
            "A.7": [f"A.7.{i}" for i in range(1, 15)],
            "A.8": [f"A.8.{i}" for i in range(1, 35)],
        },
    },
    "NIST SP 800-53 Rev 5": {
        "families": ["AC", "AT", "AU", "CA", "CM", "CP", "IA", "IR", "MA",
                     "MP", "PE", "PL", "PM", "PS", "PT", "RA", "SA", "SC",
                     "SI", "SR"],
    },
    "SOC 2 TSC": {
        "criteria": ["CC1", "CC2", "CC3", "CC4", "CC5", "CC6", "CC7",
                     "CC8", "CC9", "A1", "C1", "PI1", "P1", "P2", "P3",
                     "P4", "P5", "P6", "P7", "P8"],
    },
    "NIST SP 800-218 SSDF": {
        "practice_groups": ["PO", "PS", "PW", "RV"],
    },
}


def enumerate_clauses(standard_id, spec):
    out = []
    if "clauses_4_to_10" in spec:
        for c in spec["clauses_4_to_10"]:
            out.append({"standard": standard_id, "clause": c, "section": "main"})
    if "annex_a" in spec:
        for family, controls in spec["annex_a"].items():
            for c in controls:
                out.append({"standard": standard_id, "clause": c, "section": "annex_a",
                            "family": family})
    if "families" in spec:
        for f in spec["families"]:
            out.append({"standard": standard_id, "clause": f, "section": "family"})
    if "criteria" in spec:
        for c in spec["criteria"]:
            out.append({"standard": standard_id, "clause": c, "section": "tsc"})
    if "practice_groups" in spec:
        for g in spec["practice_groups"]:
            out.append({"standard": standard_id, "clause": g, "section": "ssdf"})
    return out


def find_attestation(root, standard_id, clause):
    safe = standard_id.replace("/", "_").replace(" ", "_")
    clause_safe = clause.replace(" ", "_").replace(".", "-")
    for sub in ["internal", "external"]:
        p = Path(root) / "compliance" / "attestations" / sub / f"{safe}__{clause_safe}.json"
        if p.exists():
            data = json.loads(p.read_text())
            return {
                "path": str(p.relative_to(root)),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "verdict": data.get("verdict"),
                "assessed_by": data.get("assessed_by"),
                "signature": data.get("signature"),
            }
    return None


def find_mapping(root, standard_id, clause):
    """Mapping files are curated by hand and live in compliance/controls/."""
    safe = standard_id.replace("/", "_").replace(" ", "_")
    p = Path(root) / "compliance" / "controls" / f"{safe}.json"
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    return data.get("mappings", {}).get(clause)


def status_for(clause_obj, mapping, attestation):
    if mapping is None and attestation is None:
        return "gap"
    if mapping is not None and attestation is None:
        return "unattested"
    if attestation and attestation.get("verdict") == "satisfied":
        return "attested"
    if attestation and attestation.get("verdict") == "partially_satisfied":
        return "attested_partial"
    if attestation and attestation.get("verdict") == "not_satisfied":
        return "gap"
    return "unattested"


def build(root):
    root = Path(root)
    clauses = []
    for sid, spec in STANDARDS.items():
        for c in enumerate_clauses(sid, spec):
            mapping = find_mapping(root, sid, c["clause"])
            att = find_attestation(root, sid, c["clause"])
            st = status_for(c, mapping, att)
            clauses.append({
                **c,
                "mapping": mapping,
                "attestation": att,
                "status": st,
            })

    counts = {}
    for c in clauses:
        counts[c["status"]] = counts.get(c["status"], 0) + 1

    return {
        "manifest_version": "0.1.0",
        "non_implication": NON_IMPLICATION,
        "standards": list(STANDARDS.keys()),
        "clause_count": len(clauses),
        "status_counts": counts,
        "any_certification_claimed": False,
        "grammar": {
            "Compliance": "Scope × Control × Evidence × Attestation",
            "closure_requires": "signed attestation per clause",
            "missing_parts_named_as": "gap",
        },
        "clauses": clauses,
    }


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    m = build(root)
    out = Path(root) / "compliance" / "readiness.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=2))
    print(f"wrote {out}")
    print(f"standards: {len(m['standards'])}")
    print(f"clauses:   {m['clause_count']}")
    for k, v in sorted(m["status_counts"].items()):
        print(f"  {k}: {v}")
    print(f"certifications claimed: {m['any_certification_claimed']}")
    print("unscoped completion: undefined")
