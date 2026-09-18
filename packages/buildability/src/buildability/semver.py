"""Semantic versioning across spec changes."""
from __future__ import annotations
from .model import Spec


def _interface_names(s: Spec) -> set:
    return {i.name for i in s.interfaces}


def _invariant_names(s: Spec) -> set:
    return {v.name for v in s.invariants}


def bump(old: Spec, new: Spec) -> str:
    """Return the semver bump between two specs.

    major: a component, interface, or invariant was removed
    minor: a component, interface, or invariant was added
    patch: only content changed
    """
    old_if = _interface_names(old)
    new_if = _interface_names(new)
    old_comp = {c.name for c in old.components}
    new_comp = {c.name for c in new.components}
    old_inv = _invariant_names(old)
    new_inv = _invariant_names(new)

    if (old_if - new_if) or (old_comp - new_comp) or (old_inv - new_inv):
        return "major"
    if (new_if - old_if) or (new_comp - old_comp) or (new_inv - old_inv):
        return "minor"
    return "patch"
