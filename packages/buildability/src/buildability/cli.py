"""CLI: evaluate a JSON spec and print the verdict."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .model import Spec, Component, Interface, Invariant, Lifecycle, Gap
from .procedure import evaluate


def load_spec(path: Path) -> Spec:
    raw = json.loads(path.read_text())
    return Spec(
        name=raw["name"],
        components=[Component(**c) for c in raw.get("components", [])],
        interfaces=[Interface(**i) for i in raw.get("interfaces", [])],
        invariants=[Invariant(**v) for v in raw.get("invariants", [])],
        lifecycle=Lifecycle(**raw["lifecycle"]) if raw.get("lifecycle") else None,
        substrate=raw.get("substrate"),
        substrate_available=raw.get("substrate_available", False),
        gaps=[Gap(**g) for g in raw.get("gaps", [])],
    )


def main(argv=None):
    ap = argparse.ArgumentParser(prog="buildability")
    ap.add_argument("spec", type=Path, help="path to spec JSON")
    ap.add_argument("--gap-history", type=int, nargs="*", default=None,
                    help="open-gap counts, oldest first")
    args = ap.parse_args(argv)

    spec = load_spec(args.spec)
    verdict = evaluate(spec, gap_history=args.gap_history)
    print(verdict)
    return 0 if verdict.regime.value == "BUILDABLE" else 1


if __name__ == "__main__":
    sys.exit(main())
