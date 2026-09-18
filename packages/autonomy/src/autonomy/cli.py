"""CLI for the autonomy evaluator.

Usage:
    python -m autonomy.cli decide --scope ops --level high --action auto_scale \
        --confidence 0.995 --blast-radius 1 --reversibility seconds
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from .contract import load_contract
from .evaluator import evaluate, Action, Context
from .audit import AuditLog

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "security" / "autonomy_contract.yaml"
AUDIT_PATH = Path(__file__).resolve().parents[4] / "security" / "autonomy_audit.jsonl"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="autonomy")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("decide")
    d.add_argument("--scope", required=True)
    d.add_argument("--level", required=True)
    d.add_argument("--action", required=True)
    d.add_argument("--confidence", type=float, default=0.0)
    d.add_argument("--blast-radius", type=int, default=0)
    d.add_argument("--reversibility", default="unknown")
    d.add_argument("--no-audit", action="store_true")

    args = ap.parse_args(argv)
    if args.cmd == "decide":
        # Runtime kill switch: the presence of the file blocks everything.
        kill_switch = CONTRACT_PATH.parent / "KILL_SWITCH"
        if kill_switch.exists():
            import json as _json
            print(_json.dumps({
                "allowed": False,
                "reason": f"kill switch engaged: {kill_switch}",
                "checked": ["kill_switch_file"],
                "failed": "kill_switch_file",
            }, indent=2))
            return 1
        contract = load_contract(CONTRACT_PATH)
        audit = AuditLog(AUDIT_PATH, enabled=not args.no_audit)
        ctx = Context(
            confidence=args.confidence,
            blast_radius=args.blast_radius,
            reversibility=args.reversibility,
        )
        action = Action(args.action, args.scope, args.level)
        d = evaluate(action, ctx, contract, audit)
        print(json.dumps({
            "allowed": d.allowed,
            "reason": d.reason,
            "checked": list(d.checked),
            "failed": d.failed,
        }, indent=2))
        return 0 if d.allowed else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
