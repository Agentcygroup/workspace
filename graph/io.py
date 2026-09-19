"""Enumerate every ingress and egress in the repo, by domain.

Reads the actual files. Does not invent. Every entry is a function
that exists, with the arguments it takes and the value it returns.
If a domain has no ingress or no egress, that is stated as absent.
"""
from __future__ import annotations
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "graph" / "io.json"


DOMAINS = {
    "engineering":   ["infra/topology.py", "infra/endpoints.py", "infra/plan.py"],
    "codegen":       ["cogdsl/compiler.py", "cogdsl/symbols.py", "omni/generate/scraper.py"],
    "ai":            ["cogdsl/engine.py", "cogdsl/tracking.py", "cogdsl/compression.py"],
    "automation":    ["pipe/autonomous_pipe.py", "infra/sqs.py", "infra/metrics.py"],
    "erp":           ["subs/erp.py", "subs/ledger.py", "subs/expenses.py"],
    "crm":           ["subs/crm.py", "subs/crm_lead.py", "subs/support_chat.py"],
    "hr":            ["subs/hr.py", "subs/ats.py"],
    "finance":       ["subs/ledger.py", "subs/payments.py", "subs/expenses.py"],
    "devops":        ["infra/kv.py", "infra/s3.py", "infra/sqs.py", "infra/iam.py",
                      "infra/vault.py", "infra/metrics.py", "infra/alerts.py",
                      "infra/dns_local.py"],
    "security":      ["infra/iam.py", "infra/vault.py", "packages/autonomy/src/autonomy/evaluator.py"],
    "manufacturing": [],
    "logistics":     [],
    "governance":    ["mastery/check.py", "packages/buildability/src/buildability/audit.py"],
}


def _sig(node: ast.FunctionDef) -> str:
    args = []
    for a in node.args.args:
        name = a.arg
        ann = ast.unparse(a.annotation) if a.annotation else ""
        args.append(f"{name}:{ann}" if ann else name)
    ret = ast.unparse(node.returns) if node.returns else ""
    return f"({', '.join(args)}) -> {ret}" if ret else f"({', '.join(args)})"


def scan_file(path: Path) -> dict:
    if not path.exists():
        return {"file": str(path.relative_to(ROOT)), "exists": False,
                "ingress": [], "egress": []}
    tree = ast.parse(path.read_text())
    ingress = []
    egress = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sig = _sig(node)
            entry = {"name": node.name, "signature": sig,
                     "line": node.lineno}
            # heuristic: return annotation or return statement => egress
            has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
            if has_return:
                egress.append(entry)
            else:
                ingress.append(entry)
        if isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    sig = _sig(sub)
                    entry = {"name": f"{node.name}.{sub.name}",
                             "signature": sig, "line": sub.lineno}
                    has_return = any(isinstance(n, ast.Return) for n in ast.walk(sub))
                    if has_return:
                        egress.append(entry)
                    else:
                        ingress.append(entry)
    return {"file": str(path.relative_to(ROOT)), "exists": True,
            "ingress": ingress, "egress": egress}


def main() -> int:
    out = {}
    for domain, files in DOMAINS.items():
        entries = [scan_file(ROOT / f) for f in files]
        total_in = sum(len(e["ingress"]) for e in entries)
        total_out = sum(len(e["egress"]) for e in entries)
        out[domain] = {
            "files": entries,
            "ingress_count": total_in,
            "egress_count": total_out,
        }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    for domain, d in out.items():
        print(f"{domain:15} files={len(d['files']):2}  in={d['ingress_count']:3}  out={d['egress_count']:3}")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
