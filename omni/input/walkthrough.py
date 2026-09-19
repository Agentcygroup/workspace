"""Walkthrough adapter. Refuses with a named reason.

A working walkthrough adapter requires a Ray-Ban Meta glasses capture
stream. That hardware is not in this repo. Rather than pretend, this
adapter refuses with a reason a caller can act on.
"""
from __future__ import annotations
from .. import RawInput


def adapt(value) -> RawInput:
    raise RuntimeError("input.walkthrough.unavailable: no capture device")
