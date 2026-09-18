"""Attest: generate standards artifacts from evidence already in the repo.

Every artifact is either derived from something measurable (git history,
test files, module docstrings, spec files) or omitted with a reason. No
fields are placeholders. If a required input is absent, the artifact is
not produced and the reason is recorded.
"""
from .generate import generate_all, ARTIFACTS
from .decisions import load_decisions, Decision
from .declared import generate_declared, DECLARED_GENERATORS
from .evidence import collect
from .report import write_report

__all__ = [
    "generate_all", "ARTIFACTS", "collect", "write_report",
    "load_decisions", "Decision", "generate_declared", "DECLARED_GENERATORS",
]
