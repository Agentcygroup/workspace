"""Enterprise domain adapter. Not an ERP. A conforming envelope emitter."""
__version__ = "0.1.0"
from ..envelope import make_envelope

def emit(env_id, entity, fact, provenance=None):
    return make_envelope(
        env_id=env_id,
        domain="enterprise",
        native_schema="fact.v1",
        payload={"entity": entity, "fact": fact},
        units={},
        preserved=["provenance", "source_hash"],
        provenance=provenance or [],
    )
