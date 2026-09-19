"""Voice adapter. Refuses with a named reason.

A working voice adapter requires a Whisper model on disk. That model
is not in this repo. Rather than pretend, this adapter refuses with
a reason a caller can act on.
"""
from __future__ import annotations
from .. import RawInput


def adapt(value) -> RawInput:
    raise RuntimeError("input.voice.unavailable: no whisper model on disk")
