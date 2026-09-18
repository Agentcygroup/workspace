"""Extract claims. Same as before, plus: every value in every artifact
that makes an assertion, not just the top-level conformant flag."""
from __future__ import annotations
import ast
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Claim:
    id: str
    source: str
    kind: str
    text: str
    evidence_needed: str
    evidence_found: bool = False
    evidence_where: str = ""
    attestable: bool = True   # False => nobody has wired a check


def collect_claims(root: Path) -> list[Claim]:
    claims: list[Claim] = []

    # ---- Standards artifacts ----------------------------------------------
    std = root / "standards"
    if std.exists():
        for p in sorted(std.glob("*.json")):
            if p.name in ("INDEX.json", "attestation_gaps.json"):
                continue
            try:
                d = json.loads(p.read_text())
            except Exception:
                continue
            for field_name in ("conformant",):
                if d.get(field_name) is True:
                    claims.append(Claim(
                        id=f"standards:{p.stem}:{field_name}",
                        source=str(p.relative_to(root)),
                        kind="conformant",
                        text=f"{p.stem}.{field_name} is true",
                        evidence_needed=(
                            "artifact is re-derivable from current repo state "
                            "and its own evidence fields still hold"
                        ),
                    ))
            if "count" in d and "verified" in d and d["count"] == d["verified"]:
                claims.append(Claim(
                    id=f"standards:{p.stem}:all-verified",
                    source=str(p.relative_to(root)),
                    kind="positive",
                    text=f"{p.stem}: {d['count']}/{d['count']} verified",
                    evidence_needed=(
                        "each verification method re-runs and matches; "
                        "or a test asserts the count"
                    ),
                ))
            if d.get("status") == "generated":
                claims.append(Claim(
                    id=f"standards:{p.stem}:generated",
                    source=str(p.relative_to(root)),
                    kind="positive",
                    text=f"{p.stem} was generated",
                    evidence_needed=(
                        "re-run generator; byte-identical output"
                    ),
                ))

    # ---- INDEX ------------------------------------------------------------
    idx = std / "INDEX.json"
    if idx.exists():
        try:
            d = json.loads(idx.read_text())
            if not d.get("omitted_or_error"):
                claims.append(Claim(
                    id="standards:INDEX:no-omitted",
                    source="standards/INDEX.json",
                    kind="positive",
                    text="all standards artifacts generated",
                    evidence_needed="regenerate all and confirm none omitted",
                ))
        except Exception:
            pass

    # ---- Decisions --------------------------------------------------------
    dec = root / "decisions"
    if dec.exists():
        for p in sorted(dec.glob("*.json")):
            try:
                d = json.loads(p.read_text())
            except Exception:
                continue
            if d.get("status") == "accepted":
                claims.append(Claim(
                    id=f"decisions:{p.stem}:accepted",
                    source=str(p.relative_to(root)),
                    kind="declared",
                    text=f"{p.stem} declared by {d.get('declared_by','?')}",
                    evidence_needed="file exists, hashes stable",
                ))

    # ---- Bridge report ----------------------------------------------------
    br = root / "bridge" / "report.json"
    if br.exists():
        try:
            d = json.loads(br.read_text())
            for sec in d.get("sections", []):
                if "regimes" in sec:
                    claims.append(Claim(
                        id=f"bridge:{sec['name']}:regimes",
                        source="bridge/report.json",
                        kind="positive",
                        text=f"{sec['name']} regimes: {sec['regimes']}",
                        evidence_needed="re-classify corpus; distribution matches",
                    ))
        except Exception:
            pass

    # ---- Mesh factory report ---------------------------------------------
    mr = root / "mesh" / "report.json"
    if mr.exists():
        try:
            d = json.loads(mr.read_text())
            claims.append(Claim(
                id="mesh:report:counts",
                source="mesh/report.json",
                kind="positive",
                text=f"mesh: emitted={d.get('emitted')} refused={d.get('skipped_invalid')}",
                evidence_needed="re-run mesh/mesh.py; counts match",
            ))
        except Exception:
            pass

    # ---- Central experiment ----------------------------------------------
    outcomes_dir = root / "experiments" / "central"
    if outcomes_dir.exists():
        for p in outcomes_dir.glob("*outcome*.json"):
            try:
                d = json.loads(p.read_text())
                if d.get("run_succeeded") is True:
                    claims.append(Claim(
                        id=f"central:{p.stem}:ran",
                        source=str(p.relative_to(root)),
                        kind="positive",
                        text=f"{d.get('spec')} ran successfully",
                        evidence_needed="re-run build script; run_succeeded matches",
                    ))
                if d.get("build_succeeded") is False and "refused" in (d.get("reason") or ""):
                    claims.append(Claim(
                        id=f"central:{p.stem}:refused",
                        source=str(p.relative_to(root)),
                        kind="refused",
                        text=f"{d.get('spec')} refused by gate",
                        evidence_needed="re-evaluate spec; regime is INCOHERENT",
                    ))
            except Exception:
                pass

    # ---- Test functions ---------------------------------------------------
    for tf in (root / "packages").rglob("test_*.py"):
        try:
            tree = ast.parse(tf.read_text())
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                claims.append(Claim(
                    id=f"test:{node.name}",
                    source=str(tf.relative_to(root)),
                    kind="tested",
                    text=f"{node.name} asserts a property",
                    evidence_needed="pytest -k matches and passes",
                ))

    return claims
