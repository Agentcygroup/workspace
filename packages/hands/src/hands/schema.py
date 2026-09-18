import json
from pathlib import Path
from . import (
    HUMAN_HANDS, COLLECTIVE_HANDS, ORGANIZATIONAL_HANDS, MACHINE_HANDS,
    HYBRID_HANDS, ARCHETYPES, FUNCTIONS, WORKFLOW_STATES, EXCEPTION_STATES,
    DECISION_CLASSES, AUTHORITY_FORMS, HANDOFF_MODES, ALLOCATIONS,
    ROOT_INVARIANT, REQUIRED_WORK_FIELDS,
)

def schema():
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Work Assignment (All Hands)",
        "type": "object",
        "required": REQUIRED_WORK_FIELDS,
        "properties": {
            "state": {"enum": WORKFLOW_STATES + EXCEPTION_STATES},
            "functions": {"type": "array", "items": {"enum": FUNCTIONS}},
            "actor_modes": {"type": "array", "items": {"enum": ARCHETYPES}},
            "allocation": {"enum": ALLOCATIONS},
            "authority": {
                "type": "object",
                "properties": {
                    "grants": {"type": "array", "items": {
                        "type": "object",
                        "properties": {"form": {"enum": AUTHORITY_FORMS}},
                    }},
                },
            },
        },
        "additionalProperties": True,
    }

def build_all(dest):
    dest = Path(dest); dest.mkdir(parents=True, exist_ok=True)
    written = []
    for name, data in [
        ("human_hands.json", HUMAN_HANDS),
        ("collective_hands.json", COLLECTIVE_HANDS),
        ("organizational_hands.json", ORGANIZATIONAL_HANDS),
        ("machine_hands.json", MACHINE_HANDS),
        ("hybrid_hands.json", HYBRID_HANDS),
        ("archetypes.json", ARCHETYPES),
        ("functions.json", FUNCTIONS),
        ("workflow_states.json", WORKFLOW_STATES),
        ("exception_states.json", EXCEPTION_STATES),
        ("decision_classes.json", DECISION_CLASSES),
        ("authority_forms.json", AUTHORITY_FORMS),
        ("handoff_modes.json", HANDOFF_MODES),
        ("allocations.json", ALLOCATIONS),
        ("root_invariant.json", ROOT_INVARIANT),
    ]:
        p = dest / name
        p.write_text(json.dumps(data, indent=2))
        written.append(str(p))
    p = dest / "work_assignment.schema.json"
    p.write_text(json.dumps(schema(), indent=2))
    written.append(str(p))
    return written
