"""Mastery beneath S by E: Federation onboarding.

Requires: ('infra/iam.py', 'infra/vault.py')
Proves:   python infra/iam.py && python infra/vault.py
Refuses:  a federation with no identity
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='S by E',
    intent='Federation onboarding',
    requires=('infra/iam.py', 'infra/vault.py'),
    proves='python infra/iam.py && python infra/vault.py',
    refuses='a federation with no identity',
)
