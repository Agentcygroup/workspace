"""Mastery beneath SE: Service publication.

Requires: ('infra/endpoints.json',)
Proves:   python infra/endpoints.py
Refuses:  a service that publishes no endpoint
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='SE',
    intent='Service publication',
    requires=('infra/endpoints.json',),
    proves='python infra/endpoints.py',
    refuses='a service that publishes no endpoint',
)
