"""Emits a declarative record module from a spec with status=specified."""
import re
from pathlib import Path

SAFE = re.compile(r"^[A-Z][A-Z0-9_]*$")

def _class_name(name):
    if not SAFE.match(name):
        raise ValueError("name not a safe identifier: " + name)
    return "".join(p.capitalize() for p in name.split("_"))

def _module_name(name):
    return name.lower()

def emit(spec, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cls = _class_name(spec["name"])
    mod = _module_name(spec["name"])
    p = outdir / (mod + ".py")
    body = f"""\"\"\"Auto-generated record for {spec['kind_id']}.\"\"\"
class {cls}:
    kind_id = \"{spec['kind_id']}\"
    level = \"{spec['level']}\"
    name = \"{spec['name']}\"
    def validate(self): return []
    def to_dict(self): return {{"kind_id": self.kind_id, "level": self.level, "name": self.name}}
"""
    p.write_text(body)
    return [str(p)]
