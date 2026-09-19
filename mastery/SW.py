"""Mastery beneath SW: Cross-domain assurance.

Requires: ('packages/buildability/tests/test_cross_spec.py',)
Proves:   python -m pytest packages/buildability/tests/test_cross_spec.py -q
Refuses:  a domain with no cross-domain test
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='SW',
    intent='Cross-domain assurance',
    requires=('packages/buildability/tests/test_cross_spec.py',),
    proves='python -m pytest packages/buildability/tests/test_cross_spec.py -q',
    refuses='a domain with no cross-domain test',
)
