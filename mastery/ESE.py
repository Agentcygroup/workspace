"""Mastery beneath ESE: Deployment preparation.

Requires: ('web/serve.py', 'cli/sovereign')
Proves:   python -c "import ast; ast.parse(open('web/serve.py').read())"
Refuses:  a deployment with no serve entry
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='ESE',
    intent='Deployment preparation',
    requires=('web/serve.py', 'cli/sovereign'),
    proves='python -c "import ast; ast.parse(open(\'web/serve.py\').read())"',
    refuses='a deployment with no serve entry',
)
