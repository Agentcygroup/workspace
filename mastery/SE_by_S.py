"""Mastery beneath SE by S: Environment integration.

Requires: ('infra/kv.py', 'infra/sqs.py', 'infra/s3.py')
Proves:   python infra/kv.py && python infra/sqs.py && python infra/s3.py
Refuses:  an environment with no store
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='SE by S',
    intent='Environment integration',
    requires=('infra/kv.py', 'infra/sqs.py', 'infra/s3.py'),
    proves='python infra/kv.py && python infra/sqs.py && python infra/s3.py',
    refuses='an environment with no store',
)
