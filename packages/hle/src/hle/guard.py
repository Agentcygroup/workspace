"""Guard: refuse artifacts that ASSERT an AGI claim.

Distinguishes assertion from refusal. If a token appears in a context that
negates it ("is not AGI", "refuses_to_claim", "no AGI", "not AGI") the guard
permits it. If it appears as a standalone assertion, the guard raises.

The point of the guard is to catch claims, not to catch the word "AGI".
"""
from __future__ import annotations

ASSERTIONS = [
    "is agi",
    "achieves agi",
    "reaches agi",
    "we are agi",
    "this is agi",
    "general intelligence achieved",
    "passed hle therefore agi",
    "hle passing means agi",
]

NEGATIONS = [
    "is not agi",
    "not agi",
    "no agi",
    "refuses_to_claim",
    "refuse to claim",
    "does not claim",
    "does not name",
    "no benchmark exists",
    "not alone suggest",
]


class AGIRefusal(Exception):
    pass


def _context_of(text, idx, window=40):
    lo = max(0, idx - window)
    hi = min(len(text), idx + window)
    return text[lo:hi]


def guard(artifact_text: str) -> bool:
    low = artifact_text.lower()
    for tok in ASSERTIONS:
        start = 0
        while True:
            idx = low.find(tok, start)
            if idx < 0:
                break
            ctx = _context_of(low, idx)
            negated = any(n in ctx for n in NEGATIONS)
            if not negated:
                raise AGIRefusal(
                    "refused: artifact asserts forbidden AGI claim: " + tok
                )
            start = idx + len(tok)
    return True
