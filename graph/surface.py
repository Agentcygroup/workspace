"""A Surface is the ingress+egress of one domain.

    Surface(domain).ingress(name, **kwargs) -> result
    Surface(domain).egress(name, **kwargs) -> result

It loads graph/io.json, finds the file that defines the named function,
imports that file, and calls the function. If the domain has no file,
or the function is absent, it refuses with a named reason. It never
pretends a domain exists when it doesn't.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IO = ROOT / "graph" / "io.json"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Surface:
    def __init__(self, domain: str):
        if not IO.exists():
            raise RuntimeError("graph.io.not-built: run graph/io.py first")
        data = json.loads(IO.read_text())
        if domain not in data:
            raise ValueError(f"surface.{domain}.unknown")
        self.domain = domain
        self.spec = data[domain]
        self._files = [e for e in self.spec["files"] if e["exists"]]

    def _find(self, name: str, kind: str):
        for entry in self._files:
            for fn in entry.get(kind, []):
                if fn["name"] == name:
                    return entry, fn
        return None, None

    def ingress(self, name: str, *args, **kwargs):
        entry, fn = self._find(name, "ingress")
        if entry is None:
            raise RuntimeError(f"surface.{self.domain}.ingress.{name}.absent")
        mod = _load(ROOT / entry["file"])
        fn_obj = getattr(mod, name.split(".")[-1], None)
        if fn_obj is None:
            raise RuntimeError(f"surface.{self.domain}.ingress.{name}.not-callable")
        return fn_obj(*args, **kwargs)

    def egress(self, name: str, *args, **kwargs):
        entry, fn = self._find(name, "egress")
        if entry is None:
            raise RuntimeError(f"surface.{self.domain}.egress.{name}.absent")
        mod = _load(ROOT / entry["file"])
        fn_obj = getattr(mod, name.split(".")[-1], None)
        if fn_obj is None:
            raise RuntimeError(f"surface.{self.domain}.egress.{name}.not-callable")
        return fn_obj(*args, **kwargs)

    def summary(self) -> dict:
        return {
            "domain": self.domain,
            "files": [e["file"] for e in self._files],
            "ingress": [f["name"] for e in self._files for f in e["ingress"]],
            "egress": [f["name"] for e in self._files for f in e["egress"]],
        }


__all__ = ["Surface"]
