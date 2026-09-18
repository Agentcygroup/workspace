"""Read decisions/ and determine which standards artifacts are unlocked.

A decision file is *declared* when:
  - status == "accepted"
  - declared_by is not "unset"
  - all required fields are non-empty

Anything less is *pending*, and the artifact it unlocks is refused.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Decision:
    name: str
    path: Path
    raw: dict
    declared: bool
    missing: list


REQUIRED = {
    "security.json": [
        ("status", str),
        ("declared_by", str),
        ("threat_model.assets", list),
        ("threat_model.adversaries", list),
        ("threat_model.worst_outcomes", list),
    ],
    "ai_rmf.json": [
        ("status", str),
        ("declared_by", str),
        ("is_ai_system_eu_ai_act", bool),
        ("risk_tier", str),
    ],
    "sqa.json": [
        ("status", str),
        ("declared_by", str),
        ("roles", dict),
        ("review_cadence", str),
    ],
    "quality_model.json": [
        ("status", str),
        ("declared_by", str),
        ("purpose_statement", str),
        ("iso_25010_characteristics", dict),
    ],
}


def _get(d, dotted):
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def load_decisions(root: Path) -> dict[str, Decision]:
    out = {}
    dec_dir = root / "decisions"
    for fname, checks in REQUIRED.items():
        p = dec_dir / fname
        if not p.exists():
            out[fname] = Decision(fname, p, {}, False, ["file absent"])
            continue
        try:
            raw = json.loads(p.read_text())
        except Exception as e:
            out[fname] = Decision(fname, p, {}, False, [f"parse error: {e}"])
            continue
        missing = []
        for dotted, typ in checks:
            v = _get(raw, dotted)
            if v is None:
                missing.append(f"{dotted} absent")
                continue
            if not isinstance(v, typ):
                missing.append(f"{dotted} wrong type")
                continue
            if isinstance(v, (str, list, dict)) and not v:
                missing.append(f"{dotted} empty")
                continue
            if typ is str and isinstance(v, str) and v == "unset":
                missing.append(f"{dotted} is 'unset'")
        declared = (not missing) and raw.get("status") == "accepted"
        out[fname] = Decision(fname, p, raw, declared, missing)
    return out


def is_effective(name: str, decisions: dict) -> bool:
    """A decision is effective if no *effective* decision revokes it.

    Revocation chains resolve transitively. A revocation that is itself
    revoked does not revoke.
    """
    # Build reverse index: who revokes whom.
    revoked_by: dict[str, list[str]] = {}
    for d in decisions.values():
        target = getattr(d, "revokes", None)
        if target:
            revoked_by.setdefault(target, []).append(d.name)

    seen = set()
    stack = [name]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        for revoker in revoked_by.get(current, []):
            if is_effective(revoker, decisions):
                return False
            stack.append(revoker)
    return True
