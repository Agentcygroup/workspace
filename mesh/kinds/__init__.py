__version__ = "0.1.0"
from .engine_record import emit as emit_record
from .engine_stub import emit as emit_stub

ENGINES = {"RECORD": emit_record, "STUB": emit_stub}
DECLARATIVE_LEVELS = {"REGISTRY","LEDGER","ARTIFACT","GOVERNANCE","META"}

def engine_for(spec):
    if spec.get("status") != "specified":
        return None
    if spec["level"] in DECLARATIVE_LEVELS:
        return ENGINES["RECORD"]
    return ENGINES["STUB"]
