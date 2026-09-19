"""Mastery beneath SE by E: Operational rollout.

Requires: ('pipe/autonomous_pipe.py',)
Proves:   python pipe/autonomous_pipe.py
Refuses:  a rollout with no pipe
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='SE by E',
    intent='Operational rollout',
    requires=('pipe/autonomous_pipe.py',),
    proves='python pipe/autonomous_pipe.py',
    refuses='a rollout with no pipe',
)
