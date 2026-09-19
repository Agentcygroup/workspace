"""Mastery beneath E by S: Build assembly.

Requires: ('pyproject.toml',)
Proves:   ls packages/buildability/pyproject.toml packages/gaps/pyproject.toml
Refuses:  an assembly with no project file
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='E by S',
    intent='Build assembly',
    requires=('pyproject.toml',),
    proves='ls packages/buildability/pyproject.toml packages/gaps/pyproject.toml',
    refuses='an assembly with no project file',
)
