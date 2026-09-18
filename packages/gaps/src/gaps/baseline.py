"""Baseline: record the current attestation state so regressions are detectable."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from .claims import Claim


def save_baseline(root: Path, claims: list[Claim]) -> Path:
    p = root / "packages" / "gaps" / "baseline" / "attestation_baseline.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    out = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "total": len(claims),
        "attested": sum(1 for c in claims if c.evidence_found),
        "unattested": sum(1 for c in claims if not c.evidence_found),
        "unattested_ids": sorted(c.id for c in claims if not c.evidence_found),
    }
    p.write_text(json.dumps(out, indent=2) + "\n")
    return p


def load_baseline(root: Path) -> dict:
    p = root / "packages" / "gaps" / "baseline" / "attestation_baseline.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def diff_baseline(root: Path, claims: list[Claim]) -> dict:
    base = load_baseline(root)
    current_unattested = {c.id for c in claims if not c.evidence_found}
    base_unattested = set(base.get("unattested_ids", []))
    return {
        "new_unattested": sorted(current_unattested - base_unattested),
        "newly_attested": sorted(base_unattested - current_unattested),
        "baseline_total": base.get("total"),
        "current_total": len(claims),
        "baseline_unattested": len(base_unattested),
        "current_unattested": len(current_unattested),
    }
