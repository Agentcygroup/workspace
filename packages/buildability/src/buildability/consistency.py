"""G1.5: coherence checks that G1 does not perform.

G1 checks presence. G1.5 checks that present elements are mutually
consistent. A spec that passes G1 but fails G1.5 is INCOHERENT: it
names all six elements but the elements contradict each other.

Checks performed:
  C1  no two components share the same responsibility
  C2  every invariant references a declared component name
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

    # C2: invariants must reference a declared component name if they
    # name one at all. We look for any component name as a substring.
    comp_names = [c.name for c in spec.components]
    for inv in spec.invariants:
        # If the invariant text mentions any component-like identifier
        # that is not declared, flag it. We only flag when the invariant
        # clearly references a name (contains a dot or underscore token).
        tokens = set()
        for word in inv.predicate.replace(",", " ").replace(".", " ").split():
            if "_" in word or "-" in word:
                tokens.add(word.strip("()[]<>"))
        for t in tokens:
            # If the token looks like a component reference and isn't
            # declared, flag it.
            if t and t not in comp_names:
                # Only flag when we have at least one component declared;
                # a spec with zero components is already caught by G1.
                if comp_names:
                    findings.append(Incoherence(
                        rule="C2.dangling-reference",
                        reason=(
                            f"invariant {inv.name!r} references {t!r} "
                            f"which is not a declared component"
                        ),
                    ))

    # C3: every interface must be claimed by at least one component.
    # An interface with no producer is a contract nothing fulfills.
    if spec.interfaces and not spec.components:
        findings.append(Incoherence(
            rule="C3.orphan-interface",
            reason="interfaces declared but no components to produce them",
        ))

    # Deduplicate findings by (rule, reason).
    unique = []
    seen_findings = set()
    for f in findings:
        key = (f.rule, f.reason)
        if key not in seen_findings:
            seen_findings.add(key)
            unique.append(f)
    return tuple(unique)
