"""Mastery beneath E: Implementation.

Requires: ('packages/buildability/src/buildability/__init__.py',)
Proves:   python -c "import sys; sys.path.insert(0, 'packages/buildability/src'); import buildability"
Refuses:  an implementation that does not import
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='E',
    intent='Implementation',
    requires=('packages/buildability/src/buildability/__init__.py',),
    proves='python -c "import sys; sys.path.insert(0, \'packages/buildability/src\'); import buildability"',
    refuses='an implementation that does not import',
)
