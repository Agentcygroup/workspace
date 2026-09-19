"""Mastery beneath N by W: Normative publication.

Requires: ('mesh/specs_outside/README.md', 'standards/INDEX.json')
Proves:   bash tests/coldstart.sh
Refuses:  a publication with no outside evidence
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='N by W',
    intent='Normative publication',
    requires=('mesh/specs_outside/README.md', 'standards/INDEX.json'),
    proves='bash tests/coldstart.sh',
    refuses='a publication with no outside evidence',
)
