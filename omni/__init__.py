"""Sovereign OmniHub.

A dispatcher package. It does not implement any subsystem. Every
subsystem is imported from an existing module:

  input    -> omni.input.*      (voice, sketch, walkthrough, legacy, url)
  generate -> omni.generate.*   (scraper, legacy, sketch)
  audit    -> omni.audit        (packages/buildability + mastery + infra)
  deploy   -> omni.deploy       (web/serve.py + subs substitutes)

This file exists so `python -m omni` resolves. The CLI is omni.cli.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class RawInput:
    """Output of an omni.input adapter."""
    kind: str                       # "url" | "legacy" | "sketch" | "voice" | "walkthrough"
    source: str                     # where the input came from (path, URL, device id)
    payload: object = None          # whatever the adapter extracted
    notes: tuple[str, ...] = ()     # non-fatal observations


@dataclass(frozen=True)
class Generated:
    """Output of an omni.generate generator."""
    kind: str                       # "app" | "store" | "dataset" | "scaffold"
    spec: dict = field(default_factory=dict)
    files: tuple[tuple[str, str], ...] = ()   # (relative_path, content)
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class AuditResult:
    """Output of omni.audit."""
    passed: bool
    regime: str = ""
    rule: str = ""                  # the specific check that failed, if any
    reason: str = ""
    checks: tuple[tuple[str, bool, str], ...] = ()   # (name, passed, reason)


@dataclass(frozen=True)
class DeployResult:
    """Output of omni.deploy."""
    target: str
    path: Path
    url: str = ""
    served: bool = False


__all__ = [
    "REPO_ROOT",
    "RawInput", "Generated", "AuditResult", "DeployResult",
]
