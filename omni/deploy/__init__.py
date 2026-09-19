"""omni.deploy: dispatch a Generated artifact to a target."""
from __future__ import annotations
import sys
from pathlib import Path
from .. import REPO_ROOT, Generated, DeployResult


TARGETS = ("localhost", "netlify", "vercel", "pinata", "ipfs", "standalone")


def _write_files(base: Path, generated: Generated) -> list[str]:
    written = []
    for rel, content in generated.files:
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        written.append(str(p.relative_to(REPO_ROOT)))
    return written


def _deploy_localhost(generated: Generated) -> DeployResult:
    base = REPO_ROOT / "web" / "frontend" / "generated"
    written = _write_files(base, generated)
    return DeployResult(
        target="localhost", path=base,
        url="http://127.0.0.1:8766/generated/",
        served=False,
    )


def _deploy_netlify(generated: Generated) -> DeployResult:
    base = REPO_ROOT / "public"
    written = _write_files(base, generated)
    return DeployResult(target="netlify", path=base, url="", served=False)


def _deploy_vercel(generated: Generated) -> DeployResult:
    base = REPO_ROOT / ".vercel" / "output"
    written = _write_files(base, generated)
    return DeployResult(target="vercel", path=base, url="", served=False)


def _deploy_pinata(generated: Generated) -> DeployResult:
    sys.path.insert(0, str(REPO_ROOT / "pin"))
    from pinata_local import pin
    hashes = []
    for rel, content in generated.files:
        h = pin(content.encode(), name=rel)
        hashes.append(h)
    return DeployResult(
        target="pinata", path=REPO_ROOT / "pin" / "pins",
        url=f"ipfs://{hashes[0]}" if hashes else "",
        served=False,
    )


def _deploy_ipfs(generated: Generated) -> DeployResult:
    return _deploy_pinata(generated)


def _deploy_standalone(generated: Generated) -> DeployResult:
    base = REPO_ROOT / "dist" / "standalone"
    written = _write_files(base, generated)
    return DeployResult(target="standalone", path=base, url="", served=False)


DISPATCH = {
    "localhost": _deploy_localhost,
    "netlify": _deploy_netlify,
    "vercel": _deploy_vercel,
    "pinata": _deploy_pinata,
    "ipfs": _deploy_ipfs,
    "standalone": _deploy_standalone,
}


def deploy(generated: Generated, target: str) -> DeployResult:
    if target not in DISPATCH:
        raise ValueError(f"deploy.{target}.unknown")
    return DISPATCH[target](generated)


__all__ = ["deploy", "DeployResult", "TARGETS"]
