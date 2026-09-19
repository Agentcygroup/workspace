"""Mastery beneath NW by N: Framework improvement.

Requires: ('packages/buildability/src/buildability/gap_history.py',)
Proves:   python -c "import sys; sys.path.insert(0, 'packages/buildability/src'); from buildability.gap_history import order_by_severity"
Refuses:  an improvement with no gap ordering
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='NW by N',
    intent='Framework improvement',
    requires=('packages/buildability/src/buildability/gap_history.py',),
    proves='python -c "import sys; sys.path.insert(0, \'packages/buildability/src\'); from buildability.gap_history import order_by_severity"',
    refuses='an improvement with no gap ordering',
)
