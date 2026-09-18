"""CLI entry: python -m attest.decide [interactive|apply|status]

  interactive  walk each pending decision, prompt for fields
  apply FILE   read FILE (JSON with field answers) and apply it
  status       print the pending/declared state without changing anything
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from .interview import interview_interactive, interview_one
from .decisions import load_decisions, REQUIRED


def main(argv=None):
    argv = argv or sys.argv[1:]
    root = Path.cwd()
    if not argv:
        cmd = "status"
    else:
        cmd = argv[0]

    if cmd == "interactive":
        interview_interactive(root)
        return 0
    if cmd == "status":
        decisions = load_decisions(root)
        for name, d in sorted(decisions.items()):
            if d.declared:
                print(f"declared   {name}")
            else:
                print(f"pending    {name}")
                for m in d.missing:
                    print(f"           - {m}")
        return 0
    if cmd == "apply":
        if len(argv) < 2:
            print("usage: python -m attest.decide apply <answers.json>")
            return 2
        answers_path = Path(argv[1])
        payload = json.loads(answers_path.read_text())
        target = payload.get("target")
        if target not in REQUIRED:
            print(f"unknown target: {target}")
            return 2
        existing_path = root / "decisions" / target
        existing = json.loads(existing_path.read_text()) if existing_path.exists() else {}
        answers = payload.get("answers", {})
        result = interview_one(target, existing, answers)
        existing_path.write_text(json.dumps(result, indent=2) + "\n")
        print(f"wrote {existing_path}")
        return 0
    print(f"unknown command: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
