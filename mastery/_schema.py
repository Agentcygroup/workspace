"""Schema for a mastery file.

A mastery file declares:
  node      the twenty-eight cycle node this mastery is beneath
  intent    the canonical intent, one line
  requires  the artifacts that must exist for the mastery to hold
  proves    the self-test that shows the mastery was exercised
  refuses   the condition under which the mastery is withheld

Every mastery file imports Mastery from this module and defines ONE.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Mastery:
    node: str
    intent: str
    requires: tuple[str, ...] = ()
    proves: str = ""
    refuses: str = ""


def check(m: Mastery, root: Path) -> tuple[bool, list[str]]:
    missing = [r for r in m.requires if not (root / r).exists()]
    return (not missing, missing)
