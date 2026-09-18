"""Interactive decision interview.

For each pending decision file, ask the human the questions the file
schema requires. Write the file only on explicit confirmation. Never
default a field: if the human says "skip", the field stays empty and
the artifact stays omitted.

The human is in the loop at every field. The tool does not invent.
"""
from __future__ import annotations
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from .decisions import REQUIRED, _get


def _ask_list(prompt: str) -> list:
    """Collect a list one item per line, blank line ends."""
    print(prompt)
    print("  (one item per line, blank line to finish)")
    items = []
    while True:
        try:
            line = input("  > ").strip()
        except EOFError:
            break
        if not line:
            break
        items.append(line)
    return items


def _ask_str(prompt: str) -> str:
    try:
        return input(prompt + "\n  > ").strip()
    except EOFError:
        return ""


def _ask_bool(prompt: str):
    while True:
        try:
            raw = input(prompt + " [y/n/skip]\n  > ").strip().lower()
        except EOFError:
            return None
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        if raw in ("skip", "s", ""):
            return None


def _ask_dict(prompt: str) -> dict:
    """Collect a small dict via key=value lines."""
    print(prompt)
    print("  (key=value per line, blank line to finish)")
    out = {}
    while True:
        try:
            line = input("  > ").strip()
        except EOFError:
            break
        if not line:
            break
        if "=" not in line:
            print("  ! need key=value")
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _set(d: dict, dotted: str, value):
    parts = dotted.split(".")
    cur = d
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = value


def _get_schema_field(raw: dict, dotted: str):
    return _get(raw, dotted)


def interview_one(fname: str, existing: dict, answers: dict) -> dict:
    """Apply human-supplied answers to the existing decision file.

    `answers` is a dict of {dotted_path: value}. Missing keys leave the
    corresponding field as it was. This lets a caller drive the interview
    programmatically instead of interactively, which is how CI or a
    scripted decision would do it.
    """
    raw = json.loads(json.dumps(existing)) if existing else {}
    for dotted, value in answers.items():
        _set(raw, dotted, value)
    if answers:
        raw["declared_by"] = answers.get("declared_by", raw.get("declared_by", "unset"))
        raw["declared_at"] = answers.get("declared_at", raw.get("declared_at",
                                            datetime.now(timezone.utc).isoformat()))
        raw["status"] = "accepted"
    return raw


def interview_interactive(root: Path):
    """Prompt for each pending decision file in turn."""
    dec_dir = root / "decisions"
    dec_dir.mkdir(exist_ok=True)
    for fname in sorted(REQUIRED.keys()):
        p = dec_dir / fname
        current = json.loads(p.read_text()) if p.exists() else {}
        checks = REQUIRED[fname]

        print()
        print("=" * 64)
        print(f"decision: {fname}")
        print(f"unlocks:  {_artifact_for(fname)}")
        print("=" * 64)

        # Skip if already declared.
        missing = []
        for dotted, typ in checks:
            v = _get(current, dotted)
            if v is None or (isinstance(v, str) and v == "unset") or v == [] or v == {}:
                missing.append(dotted)
        if not missing and current.get("status") == "accepted":
            print("already accepted; skipping.")
            continue

        print("fields still needed:")
        for m in missing:
            print(f"  - {m}")
        proceed = _ask_bool("answer now?")
        if proceed is not True:
            print("skipped; artifact remains omitted.")
            continue

        answers = {}
        answers["declared_by"] = _ask_str("who is declaring this decision?")

        for dotted, typ in checks:
            if dotted in ("status", "declared_by"):
                continue
            v = _get(current, dotted)
            already = (v is not None and v != "unset" and v != [] and v != {})
            if already:
                continue
            if typ is list:
                value = _ask_list(f"{dotted} (list):")
                if value:
                    answers[dotted] = value
            elif typ is dict:
                value = _ask_dict(f"{dotted} (dict):")
                if value:
                    answers[dotted] = value
            elif typ is bool:
                value = _ask_bool(f"{dotted}?")
                if value is not None:
                    answers[dotted] = value
            else:
                value = _ask_str(f"{dotted}:")
                if value:
                    answers[dotted] = value

        if not answers or len(answers) < 2:
            print("no answers supplied; artifact remains omitted.")
            continue

        print()
        print("proposed decision file:")
        print(json.dumps(interview_one(fname, current, answers), indent=2))
        confirm = _ask_bool("write this and accept?")
        if confirm is not True:
            print("not written; artifact remains omitted.")
            continue

        # Back up the existing file before overwriting.
        if p.exists():
            backup = p.with_suffix(".json.bak")
            shutil.copy(p, backup)
        p.write_text(json.dumps(interview_one(fname, current, answers), indent=2) + "\n")
        print(f"wrote {p}")


def _artifact_for(fname: str) -> str:
    return {
        "security.json": "security_controls",
        "ai_rmf.json": "ai_rmf_profile",
        "sqa.json": "sqa_plan",
        "quality_model.json": "quality_model",
    }.get(fname, "?")
