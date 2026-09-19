"""omni.generate: three generators, one dispatcher.

    generate(raw: RawInput) -> Generated

Kinds and generators:
    url          -> omni.generate.scraper.generate    (Step 3)
    legacy       -> omni.generate.legacy.generate     (Step 4, not yet)
    sketch       -> omni.generate.sketch.generate     (Step 5, not yet)

Unknown kinds raise ValueError("generate.<kind>.unknown").
Kinds whose generator is not yet written raise
RuntimeError("generate.<kind>.not-yet: <what it will do>").

The dispatcher does not catch either. A caller sees the reason.
"""
from __future__ import annotations
from .. import RawInput, Generated

from . import scraper as _scraper


def _legacy_not_yet(raw: RawInput) -> Generated:
    raise RuntimeError(
        "generate.legacy.not-yet: "
        "will index the source tree, resolve cogdsl symbols, emit a scaffold"
    )


def _sketch_not_yet(raw: RawInput) -> Generated:
    raise RuntimeError(
        "generate.sketch.not-yet: "
        "will OCR the image, compile a cogdsl intent, emit a scaffold"
    )


GENERATORS = {
    "url": _scraper.generate,
    "legacy": _legacy_not_yet,
    "sketch": _sketch_not_yet,
}


def generate(raw: RawInput) -> Generated:
    if raw.kind not in GENERATORS:
        raise ValueError(f"generate.{raw.kind}.unknown")
    return GENERATORS[raw.kind](raw)


__all__ = ["generate", "Generated", "GENERATORS"]
