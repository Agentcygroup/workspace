"""Legacy adapter. Reads a directory of source, returns RawInput."""
from __future__ import annotations
from pathlib import Path
from .. import RawInput


SUFFIXES = {".py", ".js", ".ts", ".rb", ".go", ".java", ".cs", ".c", ".cpp", ".h"}


def adapt(value: str) -> RawInput:
    if not value:
        raise ValueError("input.legacy.empty")
    p = Path(value).expanduser().resolve()
    if not p.exists():
        raise ValueError(f"input.legacy.absent: {p}")
    if not p.is_dir():
        raise ValueError(f"input.legacy.not-dir: {p}")
    sources = [f for f in p.rglob("*") if f.is_file() and f.suffix in SUFFIXES]
    if not sources:
        raise ValueError(f"input.legacy.no-source: {p}")
    return RawInput(
        kind="legacy",
        source=str(p),
        payload={
            "root": str(p),
            "files": tuple(str(f.relative_to(p)) for f in sources),
            "count": len(sources),
        },
        notes=(f"indexed {len(sources)} source files",),
    )
