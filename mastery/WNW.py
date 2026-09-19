"""Mastery beneath WNW: Proof preparation.

Requires: ('packages/buildability/tests/test_prover_falsifiable.py',)
Proves:   python -m pytest packages/buildability/tests/test_prover_falsifiable.py -q
Refuses:  a proof with no falsifiability
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='WNW',
    intent='Proof preparation',
    requires=('packages/buildability/tests/test_prover_falsifiable.py',),
    proves='python -m pytest packages/buildability/tests/test_prover_falsifiable.py -q',
    refuses='a proof with no falsifiability',
)
