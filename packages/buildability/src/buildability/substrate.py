"""Substrate probes: check whether a declared substrate is actually available.

Each probe returns ProbeResult. If a substrate has no probe, the result is
ProbeResult(available=False, unknown=True, reason="no probe registered").
"""
from __future__ import annotations
import shutil
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class ProbeResult:
    available: bool
    unknown: bool = False
    reason: str = ""


def _probe_kubernetes() -> ProbeResult:
    kubectl = shutil.which("kubectl")
    if kubectl is None:
        return ProbeResult(False, False, "kubectl not on PATH")
    return ProbeResult(True, False, f"kubectl at {kubectl}")


def _probe_python() -> ProbeResult:
    return ProbeResult(True, False, f"python {sys.version.split()[0]}")


def _probe_local() -> ProbeResult:
    return ProbeResult(True, False, "local filesystem available")


def _probe_docker() -> ProbeResult:
    docker = shutil.which("docker")
    if docker is None:
        return ProbeResult(False, False, "docker not on PATH")
    return ProbeResult(True, False, f"docker at {docker}")


PROBES = {
    "kubernetes": _probe_kubernetes,
    "k8s":        _probe_kubernetes,
    "python":     _probe_python,
    "local":      _probe_local,
    "docker":     _probe_docker,
}


@lru_cache(maxsize=64)
def probe(name: str) -> ProbeResult:
    """Return availability of the named substrate.

    Results are cached per substrate name for the process lifetime.
    """
    fn = PROBES.get(name.lower())
    if fn is None:
        return ProbeResult(False, unknown=True, reason="no probe registered")
    return fn()
