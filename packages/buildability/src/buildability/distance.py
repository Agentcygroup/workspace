"""Distance metric between specs. Value in [0, 1]."""
from __future__ import annotations
from .model import Spec


def _set_distance(a, b):
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return 1.0 - len(a & b) / len(union)


def _component_keys(spec):
    return {(c.name, c.responsibility) for c in spec.components}


def _interface_keys(spec):
    return {(i.name, i.schema, i.protocol, i.version) for i in spec.interfaces}


def _invariant_keys(spec):
    return {(v.name, v.predicate) for v in spec.invariants}


def _lifecycle_key(spec):
    lc = spec.lifecycle
    if lc is None:
        return ""
    return f"{lc.create}|{lc.update}|{lc.migrate}|{lc.delete}|{lc.rollback}"


def spec_distance(a: Spec, b: Spec) -> float:
    parts = [
        _set_distance(_component_keys(a), _component_keys(b)),
        _set_distance(_interface_keys(a), _interface_keys(b)),
        _set_distance(_invariant_keys(a), _invariant_keys(b)),
        0.0 if _lifecycle_key(a) == _lifecycle_key(b) else 1.0,
        0.0 if a.substrate == b.substrate else 1.0,
    ]
    return sum(parts) / len(parts)
