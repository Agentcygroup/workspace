"""Sketch adapter. Reads an image path, returns RawInput.

The OCR step is not implemented here — it lives behind the search
index and the cogdsl intent parser. This adapter's job is to verify
the image exists and is a plausible image, then hand off.
"""
from __future__ import annotations
from pathlib import Path
from .. import RawInput


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".heic", ".webp", ".tif", ".tiff", ".bmp"}


def adapt(value: str) -> RawInput:
    if not value:
        raise ValueError("input.sketch.empty")
    p = Path(value).expanduser().resolve()
    if not p.exists():
        raise ValueError(f"input.sketch.absent: {p}")
    if not p.is_file():
        raise ValueError(f"input.sketch.not-file: {p}")
    if p.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError(f"input.sketch.not-image: {p.suffix}")
    return RawInput(
        kind="sketch",
        source=str(p),
        payload={
            "path": str(p),
            "suffix": p.suffix.lower(),
            "size": p.stat().st_size,
        },
        notes=("OCR not yet wired; see step 5",),
    )
