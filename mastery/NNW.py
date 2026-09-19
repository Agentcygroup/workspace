"""Mastery beneath NNW: Consolidation of knowledge.

Requires: ('standards/INDEX.json', 'mastery')
Proves:   ls standards/INDEX.json mastery/
Refuses:  a consolidation with no index and no mastery
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='NNW',
    intent='Consolidation of knowledge',
    requires=('standards/INDEX.json', 'mastery'),
    proves='ls standards/INDEX.json mastery/',
    refuses='a consolidation with no index and no mastery',
)
