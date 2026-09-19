"""Mastery beneath W by N: Structural verification.

Requires: ('scripts/namespace_check.py',)
Proves:   python scripts/namespace_check.py
Refuses:  a structure with no namespace check
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='W by N',
    intent='Structural verification',
    requires=('scripts/namespace_check.py',),
    proves='python scripts/namespace_check.py',
    refuses='a structure with no namespace check',
)
