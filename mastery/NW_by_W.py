"""Mastery beneath NW by W: Corrective analysis.

Requires: ('mesh/specs_counterexample',)
Proves:   python -m buildability.classify mesh/specs_counterexample
Refuses:  a correction with no counterexample
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='NW by W',
    intent='Corrective analysis',
    requires=('mesh/specs_counterexample',),
    proves='python -m buildability.classify mesh/specs_counterexample',
    refuses='a correction with no counterexample',
)
