"""Mastery beneath SW by S: Contract verification.

Requires: ('packages/autonomy/tests/test_contract.py',)
Proves:   python -m pytest packages/autonomy/tests -q
Refuses:  a contract with no test
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='SW by S',
    intent='Contract verification',
    requires=('packages/autonomy/tests/test_contract.py',),
    proves='python -m pytest packages/autonomy/tests -q',
    refuses='a contract with no test',
)
