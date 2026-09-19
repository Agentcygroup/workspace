"""Homeostatic kernel: a drive vector and a band check."""
from __future__ import annotations
from dataclasses import dataclass, field


PRIORITY_DRIVES = (
    "truth",
    "safety",
    "rights_agency",
    "integrity",
    "reversibility",
)

BENEFIT_DRIVES = (
    "benefit",
    "knowledge",
    "capability",
    "efficiency",
    "resilience",
    "accessibility",
    "transferability",
    "optionality",
)

ALL_DRIVES = PRIORITY_DRIVES + BENEFIT_DRIVES


BANDS = {
    "truth":            (0.9, 1.0),
    "safety":           (0.9, 1.0),
    "rights_agency":    (0.9, 1.0),
    "integrity":        (0.9, 1.0),
    "reversibility":    (0.9, 1.0),
    "benefit":          (0.3, 1.0),
    "knowledge":        (0.3, 1.0),
    "capability":       (0.3, 1.0),
    "efficiency":       (0.3, 1.0),
    "resilience":       (0.3, 1.0),
    "accessibility":    (0.3, 1.0),
    "transferability":  (0.3, 1.0),
    "optionality":      (0.3, 1.0),
}


class Refusal(Exception):
    def __init__(self, code: str, reason: str):
        super().__init__(f"{code}: {reason}")
        self.code = code
        self.reason = reason


@dataclass
class DriveVector:
    values: dict = field(default_factory=dict)

    def set(self, drive: str, value: float) -> None:
        if drive not in ALL_DRIVES:
            raise Refusal(f"homeostasis.drive.unknown.{drive}",
                          f"{drive!r} is not a declared drive")
        if not (0.0 <= value <= 1.0):
            raise Refusal(f"homeostasis.drive.out-of-range.{drive}",
                          f"value {value} not in [0,1]")
        self.values[drive] = value

    def get(self, drive: str) -> float:
        if drive not in self.values:
            raise Refusal(f"homeostasis.drive.unset.{drive}",
                          f"{drive!r} has no value; cannot ALLOW")
        return self.values[drive]


@dataclass(frozen=True)
class Verdict:
    allow: bool
    failing: tuple
    reasons: tuple
    band: dict


def evaluate(dv: DriveVector) -> Verdict:
    missing = [d for d in ALL_DRIVES if d not in dv.values]
    if missing:
        return Verdict(
            allow=False,
            failing=tuple(missing),
            reasons=tuple(f"homeostasis.drive.unset.{d}" for d in missing),
            band=dict(BANDS),
        )
    failing = []
    reasons = []
    for d in ALL_DRIVES:
        v = dv.get(d)
        low, high = BANDS[d]
        if v < low:
            failing.append(d)
            reasons.append(f"homeostasis.drive.below.{d}: {v} < {low}")
        elif v > high:
            failing.append(d)
            reasons.append(f"homeostasis.drive.above.{d}: {v} > {high}")
    return Verdict(
        allow=not failing,
        failing=tuple(failing),
        reasons=tuple(reasons),
        band=dict(BANDS),
    )


def require_allow(dv: DriveVector) -> None:
    v = evaluate(dv)
    if not v.allow:
        raise Refusal(
            "homeostasis.refuse",
            "; ".join(v.reasons) if v.reasons else "unknown",
        )


__all__ = [
    "DriveVector", "Verdict", "Refusal",
    "PRIORITY_DRIVES", "BENEFIT_DRIVES", "ALL_DRIVES", "BANDS",
    "evaluate", "require_allow",
]
