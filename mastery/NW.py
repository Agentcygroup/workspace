"""Mastery beneath NW: Specification refinement.

Requires: ('packages/buildability/src/buildability/consistency.py',)
Proves:   python -m pytest packages/buildability/tests/test_strict.py -q
Refuses:  a refinement with no coherence rule
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='NW',
    intent='Specification refinement',
    requires=('packages/buildability/src/buildability/consistency.py',),
    proves='python -m pytest packages/buildability/tests/test_strict.py -q',
    refuses='a refinement with no coherence rule',
)
