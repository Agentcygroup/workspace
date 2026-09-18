"""Generate standards artifacts from declared decisions.

Each generator fires only if its decision file is declared. Otherwise it
returns an omitted record with the reason. No artifact is invented.
"""
from __future__ import annotations
from .decisions import Decision


CONTROL_MAP = {
    "authentication": ["NIST SP 800-53 IA", "ISO 27002 5.15"],
    "authorization":  ["NIST SP 800-53 AC", "ISO 27002 5.15"],
    "audit_log":      ["NIST SP 800-53 AU", "ISO 27002 8.15"],
    "input_validation": ["NIST SP 800-53 SI", "ISO 27002 8.28"],
    "integrity":      ["NIST SP 800-53 SI-7", "ISO 27002 8.24"],
    "supply_chain":   ["NIST SP 800-161", "ISO 27002 5.21"],
}


def security_controls(d: Decision) -> dict:
    if not d.declared:
        return {"status": "omitted", "reason": "; ".join(d.missing)}
    tm = d.raw["threat_model"]
    controls = d.raw.get("controls_applied", [])
    mapping = []
    for c in controls:
        mapping.append({
            "control": c,
            "frameworks": CONTROL_MAP.get(c, ["unmapped"]),
        })
    unmapped = [m["control"] for m in mapping if m["frameworks"] == ["unmapped"]]
    return {
        "status": "generated",
        "declared_by": d.raw["declared_by"],
        "assets": tm["assets"],
        "adversaries": tm["adversaries"],
        "worst_outcomes": tm["worst_outcomes"],
        "controls": mapping,
        "unmapped_controls": unmapped,
        "conformant": not unmapped and bool(mapping),
    }


def ai_rmf_profile(d: Decision) -> dict:
    if not d.declared:
        return {"status": "omitted", "reason": "; ".join(d.missing)}
    return {
        "status": "generated",
        "declared_by": d.raw["declared_by"],
        "is_ai_system_eu_ai_act": d.raw["is_ai_system_eu_ai_act"],
        "rationale": d.raw.get("rationale", ""),
        "risk_tier": d.raw["risk_tier"],
        "nist_ai_rmf_profile": d.raw.get("nist_ai_rmf_profile"),
        "functions": ["GOVERN", "MAP", "MEASURE", "MANAGE"],
    }


def sqa_plan(d: Decision) -> dict:
    if not d.declared:
        return {"status": "omitted", "reason": "; ".join(d.missing)}
    return {
        "status": "generated",
        "declared_by": d.raw["declared_by"],
        "roles": d.raw["roles"],
        "review_cadence": d.raw["review_cadence"],
        "release_criteria": d.raw.get("release_criteria", []),
    }


def quality_model(d: Decision) -> dict:
    if not d.declared:
        return {"status": "omitted", "reason": "; ".join(d.missing)}
    chars = d.raw["iso_25010_characteristics"]
    thresholds = d.raw.get("acceptance_thresholds", {})
    unmet = [c for c in chars if c not in thresholds]
    return {
        "status": "generated",
        "declared_by": d.raw["declared_by"],
        "purpose_statement": d.raw["purpose_statement"],
        "characteristics": chars,
        "thresholds": thresholds,
        "characteristics_without_threshold": unmet,
        "conformant": not unmet and bool(chars),
    }


DECLARED_GENERATORS = {
    "security_controls": ("security.json", security_controls),
    "ai_rmf_profile":    ("ai_rmf.json", ai_rmf_profile),
    "sqa_plan":          ("sqa.json", sqa_plan),
    "quality_model":     ("quality_model.json", quality_model),
}


def generate_declared(decisions: dict) -> dict:
    out = {}
    for artifact, (fname, fn) in DECLARED_GENERATORS.items():
        d = decisions.get(fname)
        if d is None:
            out[artifact] = {"status": "omitted", "reason": f"{fname} not loaded"}
        else:
            out[artifact] = fn(d)
    return out
