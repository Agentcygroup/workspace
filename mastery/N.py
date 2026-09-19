"""Mastery beneath N: Canonical intent.

Requires: ('specs', 'mesh/specs_uci')
Proves:   python -m buildability.classify mesh/specs_uci
Refuses:  a corpus that has no specs
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='N',
    intent='Canonical intent',
    requires=('specs', 'mesh/specs_uci'),
    proves='python -m buildability.classify mesh/specs_uci',
    refuses='a corpus that has no specs',
)
