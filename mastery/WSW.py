"""Mastery beneath WSW: Monitoring and auditing.

Requires: ('standards/http_log.jsonl', 'infra/metrics.jsonl')
Proves:   ls standards/http_log.jsonl infra/metrics.jsonl 2>&1
Refuses:  a monitor with no log
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _schema import Mastery

ONE = Mastery(
    node='WSW',
    intent='Monitoring and auditing',
    requires=('standards/http_log.jsonl', 'infra/metrics.jsonl'),
    proves='ls standards/http_log.jsonl infra/metrics.jsonl 2>&1',
    refuses='a monitor with no log',
)
