"""Step 1: prove the package is importable.

The full CLI is Step 11. This stub exists so `python -m omni` does
not fail with "No module named omni" before the CLI is written.
It refuses with a specific reason, which is the same discipline the
rest of the repo uses.
"""
from __future__ import annotations
import sys
from . import RawInput, Generated, AuditResult, DeployResult


def main() -> int:
    print("omni: package imports; CLI not implemented (Step 11)")
    print(f"omni: RawInput={RawInput.__name__}, "
          f"Generated={Generated.__name__}, "
          f"AuditResult={AuditResult.__name__}, "
          f"DeployResult={DeployResult.__name__}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
