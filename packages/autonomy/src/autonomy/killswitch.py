"""Kill switch registry.

A kill switch is a named boolean. If any kill switch associated with a
level is active, that level is closed for autonomous action.
"""
from __future__ import annotations
from dataclasses import dataclass
from .contract import Contract


@dataclass(frozen=True)
class KillSwitch:
    name: str
    active: bool


def read_kill_switches(contract: Contract) -> dict[str, KillSwitch]:
    return {name: KillSwitch(name, active) for name, active in contract.kill_switches.items()}


def any_active(names: tuple[str, ...], switches: dict[str, KillSwitch]) -> tuple[bool, str]:
    for name in names:
        ks = switches.get(name)
        if ks is None:
            return True, f"unknown kill switch {name!r}"
        if ks.active:
            return True, f"kill switch active: {name}"
    return False, ""
