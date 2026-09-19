"""The twenty-eight masteries, discovered by module name."""
from pathlib import Path
import importlib

HERE = Path(__file__).resolve().parent


def discover():
    out = {}
    for p in sorted(HERE.glob("*.py")):
        if p.stem.startswith("_"):
            continue
        mod = importlib.import_module(f"mastery.{p.stem}")
        if hasattr(mod, "ONE"):
            out[p.stem] = mod.ONE
    return out
