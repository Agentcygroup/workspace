"""Mastery beneath W: Conformance assessment.

Requires: ('standards/INDEX.json', 'scripts/verify.sh')
Proves:   ./scripts/verify.sh
Refuses:  a conformance with no index
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='W',
    intent='Conformance assessment',
    requires=('standards/INDEX.json', 'scripts/verify.sh'),
    proves='./scripts/verify.sh',
    refuses='a conformance with no index',
)
