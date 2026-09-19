"""omni.input: five adapters, one dispatcher.

    adapt(kind, value) -> RawInput

Kinds:
    url          -> omni.input.url.adapt
    legacy       -> omni.input.legacy.adapt
    sketch       -> omni.input.sketch.adapt
    voice        -> omni.input.voice.adapt      (refuses: no whisper model)
    walkthrough  -> omni.input.walkthrough.adapt (refuses: no capture device)

Unknown kinds raise ValueError("input.<kind>.unknown"). Adapters raise
ValueError for malformed input and RuntimeError for missing capability.
The dispatcher does not catch either; a caller sees the specific reason.
"""
from __future__ import annotations
from .. import RawInput

from . import url as _url
from . import legacy as _legacy
from . import sketch as _sketch
from . import voice as _voice
from . import walkthrough as _walkthrough


ADAPTERS = {
    "url": _url.adapt,
    "legacy": _legacy.adapt,
    "sketch": _sketch.adapt,
    "voice": _voice.adapt,
    "walkthrough": _walkthrough.adapt,
}


def adapt(kind: str, value) -> RawInput:
    if kind not in ADAPTERS:
        raise ValueError(f"input.{kind}.unknown")
    return ADAPTERS[kind](value)


__all__ = ["adapt", "RawInput", "ADAPTERS"]
