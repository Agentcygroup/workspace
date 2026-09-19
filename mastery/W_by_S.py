"""Mastery beneath W by S: Measurement.

Requires: ('standards/composition_report.json',)
Proves:   ls standards/composition_report.json
Refuses:  a measurement with no report
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='W by S',
    intent='Measurement',
    requires=('standards/composition_report.json',),
    proves='ls standards/composition_report.json',
    refuses='a measurement with no report',
)
