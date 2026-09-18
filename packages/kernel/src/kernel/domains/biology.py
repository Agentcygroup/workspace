"""Biology domain adapter."""
__version__ = "0.1.0"
from ..envelope import make_envelope

def emit(env_id, taxon, trait, value, provenance=None):
    return make_envelope(
        env_id=env_id,
        domain="biology",
        native_schema="trait.v1",
        payload={"taxon": taxon, "trait": trait, "value": value},
        units={},
        preserved=["provenance", "source_hash"],
        provenance=provenance or [],
    )
