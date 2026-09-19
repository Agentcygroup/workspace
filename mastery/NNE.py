"""Mastery beneath NNE: Domain decomposition.

Requires: ('packages/buildability/src/buildability/models',)
Proves:   python -c "from buildability.models import MODEL_REGISTRY; print(len(MODEL_REGISTRY))"
Refuses:  a decomposition that names no model
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='NNE',
    intent='Domain decomposition',
    requires=('packages/buildability/src/buildability/models',),
    proves='python -c "from buildability.models import MODEL_REGISTRY; print(len(MODEL_REGISTRY))"',
    refuses='a decomposition that names no model',
)
