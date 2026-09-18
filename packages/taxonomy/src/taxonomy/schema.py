import json
from pathlib import Path
from . import LEVELS, KINDS, INVARIANTS, FORBIDDEN_TOKENS, level_of, is_kind, scan_forbidden

def schema_for(level_name):
    kinds = KINDS.get(level_name, [])
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": f"Level {level_of(level_name)} {level_name}",
        "type": "object",
        "required": ["level", "kind"],
        "properties": {
            "level": {"const": level_name},
            "kind": {"enum": kinds} if kinds else {"type": "string"},
            "scoped": {"const": True},
            "bound": {"type": "string"},
            "version": {"type": "string"},
            "depends_on_level": { "const": LEVELS[level_of(level_name) - 1]
                if level_of(level_name) > 0 else None },
            "defines_terms_for_level": { "const": LEVELS[level_of(level_name) + 1]
                if level_of(level_name) < len(LEVELS) - 1 else None },
        },
        "additionalProperties": True,
    }
    return schema

def build_all(dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for name in LEVELS:
        s = schema_for(name)
        p = dest / f"level_{level_of(name):02d}_{name.lower()}.schema.json"
        p.write_text(json.dumps(s, indent=2))
        written.append(str(p))
    return written

def validate_instance(instance):
    """Return (level, ok, reasons)."""
    reasons = []
    if not isinstance(instance, dict):
        return None, False, ["not an object"]
    lvl = instance.get("level")
    kind = instance.get("kind")
    if lvl not in LEVELS:
        return lvl, False, [f"unknown level: {lvl}"]
    if kind and not is_kind(lvl, kind):
        reasons.append(f"kind {kind} not in level {lvl}")
    if instance.get("scoped") is not True:
        reasons.append("instance not marked scoped:true")
    hits = scan_forbidden(instance)
    for path, tok in hits:
        reasons.append(f"forbidden token {tok!r} at {path}")
    return lvl, not reasons, reasons
