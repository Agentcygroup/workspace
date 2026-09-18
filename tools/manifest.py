#!/usr/bin/env python3
"""Produce a manifest of all files in the repo with sha256 hashes."""
import hashlib, json, os, sys
from pathlib import Path

SKIP = {".git", ".venv", "__pycache__", "build", "dist", "sbom", ".pytest_cache"}

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(8192), b""):
            h.update(c)
    return h.hexdigest()

def walk(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for name in sorted(filenames):
            p = Path(dirpath) / name
            if p.is_file():
                out.append({"path": str(p.relative_to(root)), "sha256": sha(p), "bytes": p.stat().st_size})
    return out

if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    manifest = {"root": str(root), "files": walk(root)}
    print(json.dumps(manifest, indent=2))
