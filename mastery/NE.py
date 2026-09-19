"""Mastery beneath NE: Model-driven generation.

Requires: ('packages/buildability/src/buildability/selection.py',)
Proves:   python -m pytest packages/buildability/tests/test_selection.py -q
Refuses:  a spec that declares no model
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='NE',
    intent='Model-driven generation',
    requires=('packages/buildability/src/buildability/selection.py',),
    proves='python -m pytest packages/buildability/tests/test_selection.py -q',
    refuses='a spec that declares no model',
)
