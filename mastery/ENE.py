"""Mastery beneath ENE: Service decomposition.

Requires: ('infra/connections.json', 'infra/topology.py')
Proves:   python infra/topology.py
Refuses:  a service that names no connection
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='ENE',
    intent='Service decomposition',
    requires=('infra/connections.json', 'infra/topology.py'),
    proves='python infra/topology.py',
    refuses='a service that names no connection',
)
