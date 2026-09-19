"""Mastery beneath N by E: Requirements elaboration.

Requires: ('packages/buildability/src/buildability/gates.py', 'specs')
Proves:   python -m pytest packages/buildability/tests -q
Refuses:  specs without the six-element requirement
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='N by E',
    intent='Requirements elaboration',
    requires=('packages/buildability/src/buildability/gates.py', 'specs'),
    proves='python -m pytest packages/buildability/tests -q',
    refuses='specs without the six-element requirement',
)
