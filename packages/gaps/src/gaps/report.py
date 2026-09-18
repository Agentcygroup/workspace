"""Write the gap report."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
from .claims import Claim


def write_gap_report(root: Path, claims: list[Claim]) -> dict:
    attested = [c for c in claims if c.evidence_found]
    unattested = [c for c in claims if not c.evidence_found]

    out = {
        "total_claims": len(claims),
        "attested": len(attested),
        "unattested": len(unattested),
        "by_kind": dict(Counter(c.kind for c in claims)),
        "unattested_by_kind": dict(Counter(c.kind for c in unattested)),
        "unattested": [
            {
                "id": c.id,
                "source": c.source,
                "kind": c.kind,
                "text": c.text,
                "evidence_needed": c.evidence_needed,
                "reason": c.evidence_where,
            }
            for c in unattested
        ],
    }
    p = root / "standards" / "attestation_gaps.json"
    p.write_text(json.dumps(out, indent=2, default=str) + "\n")
    return out
