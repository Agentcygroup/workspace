"""Canonical envelope: the object every domain emits and consumes."""
__version__ = "0.1.0"
import hashlib
import json
from dataclasses import dataclass, asdict, field
from typing import Any

ENVELOPE_VERSION = "0.1.0"

@dataclass(frozen=True)
class Envelope:
    id: str
    domain: str
    native_schema: str
    payload: Any
    units: dict
    preserved: list
    compat: str
    source_hash: str
    provenance: list
    schema_version: str = ENVELOPE_VERSION

    def to_dict(self):
        return asdict(self)

def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()

def _sha(b):
    return hashlib.sha256(b).hexdigest()

def make_envelope(env_id, domain, native_schema, payload, units=None,
                  preserved=None, compat="0.1.0", provenance=None):
    units = units or {}
    preserved = preserved or []
    provenance = provenance or []
    source_hash = _sha(_canon({"domain": domain, "schema": native_schema, "payload": payload}))
    return Envelope(
        id=env_id,
        domain=domain,
        native_schema=native_schema,
        payload=payload,
        units=units,
        preserved=sorted(set(preserved)),
        compat=compat,
        source_hash=source_hash,
        provenance=list(provenance),
    )

def verify_envelope(env):
    errs = []
    if not env.id: errs.append("missing id")
    if not env.domain: errs.append("missing domain")
    if not env.native_schema: errs.append("missing native_schema")
    if env.schema_version != ENVELOPE_VERSION:
        errs.append(f"schema_version {env.schema_version} != {ENVELOPE_VERSION}")
    if not isinstance(env.preserved, list):
        errs.append("preserved must be a list")
    if env.compat not in ("0.1.0",):
        errs.append(f"unsupported compat {env.compat}")
    return errs
