"""Mastery beneath S by W: Policy coordination.

Requires: ('security/autonomy_contract.yaml',)
Proves:   python -c "import sys; sys.path.insert(0, 'packages/autonomy/src'); from autonomy import load_contract; load_contract(__import__('pathlib').Path('security/autonomy_contract.yaml'))"
Refuses:  a policy with no contract
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='S by W',
    intent='Policy coordination',
    requires=('security/autonomy_contract.yaml',),
    proves='python -c "import sys; sys.path.insert(0, \'packages/autonomy/src\'); from autonomy import load_contract; load_contract(__import__(\'pathlib\').Path(\'security/autonomy_contract.yaml\'))"',
    refuses='a policy with no contract',
)
