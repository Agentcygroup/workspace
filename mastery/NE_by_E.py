"""Mastery beneath NE by E: API and contract design.

Requires: ('web/backend.py', 'web/middleware.py')
Proves:   python -m pytest web/tests/test_backend.py -q
Refuses:  an endpoint with no contract
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='NE by E',
    intent='API and contract design',
    requires=('web/backend.py', 'web/middleware.py'),
    proves='python -m pytest web/tests/test_backend.py -q',
    refuses='an endpoint with no contract',
)
