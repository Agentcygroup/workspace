"""omni CLI: --input <kind> --value <v> --target <t>."""
from __future__ import annotations
import argparse
import sys
from .input import adapt
from .generate import generate
from .audit import audit
from .deploy import deploy, TARGETS


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="omni")
    p.add_argument("--input", required=True,
                   choices=["url", "legacy", "sketch", "voice", "walkthrough"])
    p.add_argument("--value", required=True)
    p.add_argument("--target", default="localhost", choices=list(TARGETS))
    p.add_argument("--skip-audit", action="store_true")
    args = p.parse_args(argv)

    print(f"input  : {args.input} = {args.value}")

    try:
        raw = adapt(args.input, args.value)
    except (ValueError, RuntimeError) as e:
        print(f"refused: {e}")
        return 2
    print(f"adapter: {raw.kind} from {raw.source}")

    try:
        gen = generate(raw)
    except (ValueError, RuntimeError) as e:
        print(f"refused: {e}")
        return 3
    print(f"gen    : kind={gen.kind} files={len(gen.files)}")

    if not args.skip_audit:
        result = audit(gen)
        print(f"audit  : {'pass' if result.passed else 'FAIL'}")
        for name, ok, reason in result.checks:
            print(f"  {name:24} {'ok' if ok else 'FAIL':4} {reason}")
        if not result.passed:
            return 4

    dep = deploy(gen, args.target)
    print(f"deploy : target={dep.target} path={dep.path}")
    if dep.url:
        print(f"url    : {dep.url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
