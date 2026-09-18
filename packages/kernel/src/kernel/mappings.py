"""Three cross-domain mappings. Each declares what it preserves."""
__version__ = "0.1.0"
from .envelope import make_envelope

MAPPINGS = {
    "physics_to_biology": {
        "from": "physics",
        "to": "biology",
        "preserved": ["units", "provenance", "source_hash"],
        "rationale": "quantities and provenance carry; semantics do not",
    },
    "medicine_to_enterprise": {
        "from": "medicine",
        "to": "enterprise",
        "preserved": ["provenance", "source_hash"],
        "rationale": "identifiers and lineage carry; clinical meaning does not",
    },
    "robotics_to_sensor_fusion": {
        "from": "robotics",
        "to": "sensor_fusion",
        "preserved": ["units", "source_hash"],
        "rationale": "measurement units carry; control semantics do not",
    },
}

def map_envelope(env, mapping_name):
    m = MAPPINGS.get(mapping_name)
    if m is None:
        raise ValueError("unknown mapping: " + mapping_name)
    if env.domain != m["from"]:
        raise ValueError("envelope domain " + env.domain + " != " + m["from"])
    new_payload = {}
    if isinstance(env.payload, dict):
        for k in env.preserved:
            if k in env.payload:
                new_payload[k] = env.payload[k]
    new_units = env.units if "units" in m["preserved"] else {}
    return make_envelope(
        env_id=env.id + "::" + mapping_name,
        domain=m["to"],
        native_schema=env.native_schema,
        payload=new_payload,
        units=new_units,
        preserved=m["preserved"],
        compat=env.compat,
        provenance=env.provenance + ["mapped:" + mapping_name],
    )

def preservation_report(env, mapping_name):
    m = MAPPINGS.get(mapping_name) or {}
    return {"preserved": m.get("preserved", []), "rationale": m.get("rationale", "")}
