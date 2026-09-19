"""Mastery beneath SSE: Operational coordination.

Requires: ('infra/metrics.py', 'infra/alerts.py')
Proves:   python infra/metrics.py && python infra/alerts.py
Refuses:  an operation with no metric
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='SSE',
    intent='Operational coordination',
    requires=('infra/metrics.py', 'infra/alerts.py'),
    proves='python infra/metrics.py && python infra/alerts.py',
    refuses='an operation with no metric',
)
