"""Mastery beneath SW by W: Operational verification.

Requires: ('packages/gaps/gaps.py', 'packages/gaps/baseline/attestation_baseline.json')
Proves:   python packages/gaps/gaps.py --diff
Refuses:  an operation with no baseline
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='SW by W',
    intent='Operational verification',
    requires=('packages/gaps/gaps.py', 'packages/gaps/baseline/attestation_baseline.json'),
    proves='python packages/gaps/gaps.py --diff',
    refuses='an operation with no baseline',
)
