"""Mastery beneath S: Cross-domain coordination.

Requires: ('infra/dns_local.py', 'infra/plan.py')
Proves:   python infra/dns_local.py && python infra/plan.py
Refuses:  a federation with no plan
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='S',
    intent='Cross-domain coordination',
    requires=('infra/dns_local.py', 'infra/plan.py'),
    proves='python infra/dns_local.py && python infra/plan.py',
    refuses='a federation with no plan',
)
