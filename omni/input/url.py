"""URL adapter. Reads a URL, validates its shape, returns RawInput."""
from __future__ import annotations
from urllib.parse import urlparse
from .. import RawInput


def adapt(value: str) -> RawInput:
    if not value:
        raise ValueError("input.url.empty")
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"input.url.scheme: {parsed.scheme!r}")
    if not parsed.netloc:
        raise ValueError("input.url.no-netloc")
    return RawInput(
        kind="url",
        source=value,
        payload={
            "url": value,
            "scheme": parsed.scheme,
            "host": parsed.netloc,
            "path": parsed.path or "/",
        },
    )
