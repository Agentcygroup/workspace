"""Mastery beneath SSW: Organizational alignment.

Requires: ('decisions',)
Proves:   ls decisions/*.json
Refuses:  an organization with no decision on record
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='SSW',
    intent='Organizational alignment',
    requires=('decisions',),
    proves='ls decisions/*.json',
    refuses='an organization with no decision on record',
)
