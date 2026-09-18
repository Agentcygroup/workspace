import hashlib, json, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class SBOM:
    components: list = field(default_factory=list)
    def add(self, name, version="", purl="", sha256=""):
        self.components.append({"type":"library","name":name,"version":version,"purl":purl,"hashes":[{"alg":"SHA-256","content":sha256}]})
        return self.components[-1]
    def to_cyclonedx(self):
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "version": 1,
            "components": list(self.components),
        }

def generate_sbom():
    """Read installed pip packages and produce a CycloneDX SBOM dict."""
    sb = SBOM()
    try:
        out = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"],
                             capture_output=True, text=True, check=True)
        pkgs = json.loads(out.stdout)
    except Exception:
        pkgs = []
    for p in pkgs:
        sb.add(name=p.get("name",""), version=p.get("version",""))
    return sb.to_cyclonedx()
