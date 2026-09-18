import json
from pathlib import Path
from . import (AX, SCOPES, FUNCTIONS, allocation_for, categories,
               agent_capable, human_required, coverage, scope_variants)

def schema():
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "AX Allocation Entry",
        "type": "object",
        "required": ["allocation", "rationale", "agent_capable", "human_required"],
        "properties": {
            "allocation": {"enum": [
                "human_only","assisted","human_approved","human_supervised",
                "exception_supervised","dual_control","agent_executed",
                "machine_executed","multi_agent","prohibited",
            ]},
            "rationale": {"type": "string"},
            "agent_capable": {"type": "array", "items": {"type": "string"}},
            "human_required": {"type": "array", "items": {"type": "string"}},
        },
        "additionalProperties": False,
    }

def build_all(dest):
    dest = Path(dest); dest.mkdir(parents=True, exist_ok=True)
    written = []
    p = dest / "ax.json"
    p.write_text(json.dumps(AX, indent=2)); written.append(str(p))
    p = dest / "scopes.json"
    p.write_text(json.dumps(SCOPES, indent=2)); written.append(str(p))
    p = dest / "functions.json"
    p.write_text(json.dumps(FUNCTIONS, indent=2)); written.append(str(p))
    p = dest / "coverage.json"
    p.write_text(json.dumps(coverage(), indent=2)); written.append(str(p))
    p = dest / "ax.schema.json"
    p.write_text(json.dumps(schema(), indent=2)); written.append(str(p))
    p = dest / "role_scope_function_grid.json"
    grid = []
    for cat, e in AX.items():
        for role in (e.get("agent_capable", []) + e.get("human_required", [])):
            for s in SCOPES:
                for fn in FUNCTIONS:
                    grid.append({"category": cat, "role": role,
                                 "scope": s, "function": fn,
                                 "allocation": e["allocation"]})
    p.write_text(json.dumps(grid, indent=2)); written.append(str(p))
    return written
