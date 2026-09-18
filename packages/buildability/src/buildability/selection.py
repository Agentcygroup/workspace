"""Select a model for a spec based on the spec's shape."""
from __future__ import annotations
from .model import Spec
from .models import MODEL_REGISTRY


class NoSuitableModel(Exception):
    pass


def select_model(spec: Spec) -> str:
    if spec.substrate and spec.substrate.lower() in MODEL_REGISTRY:
        return spec.substrate.lower()

    protocols = {i.protocol.lower() for i in spec.interfaces}
    if "internal" in protocols or "jsonrpc" in protocols:
        return "pi"

    names = " ".join(c.name.lower() for c in spec.components)
    if "state" in names or "machine" in names:
        return "general"

    if not spec.components and not spec.interfaces:
        raise NoSuitableModel("spec has no discriminating feature")

    return "boolean"
