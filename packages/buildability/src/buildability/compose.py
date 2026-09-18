"""Cross-spec composition: check interfaces between specs."""
from __future__ import annotations
from dataclasses import dataclass
from .model import Spec
from .procedure import evaluate, Verdict


@dataclass(frozen=True)
class InterfaceMismatch:
    producer: str
    consumer: str
    interface: str
    reason: str


@dataclass(frozen=True)
class CompositionResult:
    verdicts: dict
    mismatches: tuple
    ok: bool


def _evaluate_many_original(specs):
    """Evaluate a set of specs and check pairwise interface consistency."""
    verdicts = {s.name: evaluate(s) for s in specs}

    producers = {}
    for spec in specs:
        for iface in spec.interfaces:
            producers.setdefault(iface.name, []).append((spec.name, iface))

    mismatches = []
    for spec in specs:
        for iface in spec.interfaces:
            holders = producers.get(iface.name, [])
            if len(holders) <= 1:
                continue
            first_name, first_iface = holders[0]
            for other_name, other_iface in holders[1:]:
                if (first_iface.schema != other_iface.schema
                        or first_iface.protocol != other_iface.protocol):
                    mismatches.append(InterfaceMismatch(
                        producer=first_name,
                        consumer=other_name,
                        interface=iface.name,
                        reason=(
                            "schema mismatch: "
                            + first_iface.schema + "/" + first_iface.protocol
                            + " vs "
                            + other_iface.schema + "/" + other_iface.protocol
                        ),
                    ))

    all_ok = all(
        v.regime in ("CONSTRUCTION", "BUILDABLE") for v in verdicts.values()
    )
    return CompositionResult(
        verdicts=verdicts,
        mismatches=tuple(mismatches),
        ok=all_ok and not mismatches,
    )


def evaluate_many(specs, namespace: bool = False):
    """Wraps _evaluate_many_original with an optional namespace qualifier.

    When namespace=True, every interface name is prefixed with its spec's
    name, so two specs can both declare "auth" without conflict.
    """
    if namespace:
        from dataclasses import replace as _dc_replace
        specs = [
            _dc_replace(s, interfaces=tuple(
                _dc_replace(i, name=f"{s.name}.{i.name}") for i in s.interfaces
            ))
            for s in specs
        ]
    return _evaluate_many_original(specs)
