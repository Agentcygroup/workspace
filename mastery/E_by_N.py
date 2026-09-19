"""Mastery beneath E by N: Build preparation.

Requires: ('cli/sovereign', 'scripts/verify.sh')
Proves:   ./scripts/verify.sh
Refuses:  a build with no verify step
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='E by N',
    intent='Build preparation',
    requires=('cli/sovereign', 'scripts/verify.sh'),
    proves='./scripts/verify.sh',
    refuses='a build with no verify step',
)
