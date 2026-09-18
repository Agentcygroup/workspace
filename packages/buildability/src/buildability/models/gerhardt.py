"""Gerhardt logarithmic operator.

Frequency-domain logic: magnitude, phase, and frequency each carry a
distinct logical dimension. This is analog logic, not binary.

  magnitude  -> amplitude logic    (how strong)
  phase      -> directional logic  (which way)
  frequency  -> address logic      (which channel)

The logarithmic operator is the map from a physical signal to a logic
state:  L(signal) = log(f / f_ref) + i * phase

A spec's interfaces become frequencies; a spec's components become
phase angles. The resulting logical state is a complex number whose
real part addresses and whose imaginary part orients.

Reference: Tesla, "Method of and Apparatus for Controlling Mechanism
of Moving Vessels or Vehicles" (US Patent 613,809).
"""
from __future__ import annotations
import cmath
import math
from ..model import Spec


F_REF = 1.0


def _log_operator(freq: float, phase: float) -> complex:
    """The Gerhardt logarithmic operator applied to one signal."""
    if freq <= 0:
        return complex(0.0, phase)
    return complex(math.log(freq / F_REF), phase)


def solver(spec: Spec) -> dict:
    """A candidate is a set of (frequency, phase) pairs, one per interface,
    plus a resonant frequency that addresses the spec."""
    n = max(1, len(spec.interfaces))
    channels = []
    for i, iface in enumerate(spec.interfaces):
        freq = (i + 1) * F_REF
        phase = (2 * math.pi * i) / n
        channels.append({
            "name": iface.name,
            "freq": freq,
            "phase": phase,
            "op": _log_operator(freq, phase),
        })
    resonant = sum(c["freq"] for c in channels) / n
    return {"resonant": resonant, "channels": channels, "spec": spec.name}


def prover(candidate, spec: Spec) -> bool:
    """Falsifiable: rejects candidates whose channels do not cover the
    spec's declared interfaces, or whose resonant frequency is non-positive."""
    if not isinstance(candidate, dict):
        return False
    if "channels" not in candidate or "resonant" not in candidate:
        return False
    if candidate["resonant"] <= 0:
        return False
    declared = {i.name for i in spec.interfaces}
    present = {c["name"] for c in candidate["channels"]}
    return declared.issubset(present)


def resolver(a, b):
    """Order by resonant frequency. Ties return None."""
    if a == b:
        return 0
    ra = a.get("resonant") if isinstance(a, dict) else None
    rb = b.get("resonant") if isinstance(b, dict) else None
    if ra is None or rb is None or ra == rb:
        return None
    return -1 if ra < rb else 1
