"""Mastery beneath NE by N: Architectural refinement.

Requires: ('packages/buildability/src/buildability/compose.py',)
Proves:   python -m pytest packages/buildability/tests/test_cross_spec.py -q
Refuses:  an architecture with no cross-spec interface
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='NE by N',
    intent='Architectural refinement',
    requires=('packages/buildability/src/buildability/compose.py',),
    proves='python -m pytest packages/buildability/tests/test_cross_spec.py -q',
    refuses='an architecture with no cross-spec interface',
)
