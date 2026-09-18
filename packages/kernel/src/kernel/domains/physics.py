"""Physics domain adapter. Not a physics engine. A conforming envelope emitter."""
__version__ = "0.1.0"
from ..envelope import make_envelope

def emit(env_id, observable, value, unit, provenance=None):
    return make_envelope(
        env_id=env_id,
        domain="physics",
        native_schema="observable.v1",
        payload={"observable": observable, "value": value},
        units={observable: unit},
        preserved=["units", "provenance", "source_hash"],
        provenance=provenance or [],
    )
