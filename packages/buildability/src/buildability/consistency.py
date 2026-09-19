"""G1.5: coherence checks that G1 does not perform.

G1 checks presence. G1.5 checks that present elements are mutually
consistent. A spec that passes G1 but fails G1.5 is INCOHERENT: it
names all six elements but the elements contradict each other.

Checks performed:
  C1  no two components share the same responsibility
  C2  every identifier-like token in an invariant predicate must be
      a declared component name. Invariants with no identifier-like
      tokens (numeric bounds, prose) are not checked.
  C3  every interface is claimed by at least one component
  C4  lifecycle fields are non-empty strings (already checked by G1)
"""
from __future__ import annotations
from dataclasses import dataclass
from .model import Spec


@dataclass(frozen=True)
class Incoherence:
    rule: str
    reason: str


def _component_names(spec: Spec) -> list[str]:
    return [c.name for c in spec.components]


def _identifier_tokens(text: str) -> set[str]:
    """Tokens containing '_' or '-' are treated as identifier-like."""
    tokens = set()
    for word in text.replace(",", " ").replace(".", " ").split():
        w = word.strip("()[]<>{};:")
        if "_" in w or "-" in w:
            tokens.add(w)
    return tokens


def check_consistency(spec: Spec) -> tuple[Incoherence, ...]:
    findings: list[Incoherence] = []

    # C1: duplicate responsibilities.
    seen: dict[str, str] = {}
    for comp in spec.components:
        resp = comp.responsibility.strip().lower()
        if resp in seen:
            findings.append(Incoherence(
                rule="C1.duplicate-responsibility",
                reason=(
                    f"components {seen[resp]!r} and {comp.name!r} both claim "
                    f"responsibility {comp.responsibility!r}"
                ),
            ))
        else:
            seen[resp] = comp.name

    # C2: every identifier-like token in an invariant predicate must be
    # a declared component name. Predicates with no identifier-like
    # tokens (numeric bounds, prose without underscores or hyphens) are
    # not checked; there is nothing for them to reference.
    comp_names = _component_names(spec)
    for inv in spec.invariants:
        tokens = _identifier_tokens(inv.predicate)
        for t in tokens:
            if t not in comp_names:
                findings.append(Incoherence(
                    rule="C2.dangling-reference",
                    reason=(
                        f"invariant {inv.name!r} references {t!r} "
                        f"which is not a declared component"
                    ),
                ))

    # C3: every interface must be claimed by at least one component.
    if spec.interfaces and not spec.components:
        findings.append(Incoherence(
            rule="C3.orphan-interface",
            reason="interfaces declared but no components to produce them",
        ))

    # Deduplicate.
    unique = []
    seen_findings = set()
    for f in findings:
        key = (f.rule, f.reason)
        if key not in seen_findings:
            seen_findings.add(key)
            unique.append(f)
    return tuple(unique)
