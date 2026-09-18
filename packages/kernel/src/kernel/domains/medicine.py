"""Medicine domain adapter. Not a clinical system. A conforming envelope emitter."""
__version__ = "0.1.0"
from ..envelope import make_envelope

def emit(env_id, patient_id, observation, value, provenance=None):
    return make_envelope(
        env_id=env_id,
        domain="medicine",
        native_schema="observation.v1",
        payload={"patient_id": patient_id, "observation": observation, "value": value},
        units={},
        preserved=["provenance", "source_hash"],
        provenance=provenance or [],
    )
