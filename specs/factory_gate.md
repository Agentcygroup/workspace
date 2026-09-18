# Specification: Factory Gate Integration

## Artifact
The `mesh/mesh.py` emit loop must consult `_gate()` before calling
`engine_for()`. A spec whose regime is RESEARCH, INCOHERENT, or DIVERGENT
must be refused with a reason and must not produce output files.

## Interface
    def _gate(spec: dict) -> str | None:
        # returns regime name if refused, None if allowed

    for s in specs:
        if s.get("status") != "specified":
            continue
        reason = _gate(s)
        if reason:
            report["skipped_invalid"] += 1
            report["errors"].append({"kind_id": s["kind_id"], "error": reason})
            continue
        eng = engine_for(s)
        ...

## Evidence
- `mesh/report.json` shows `skipped_invalid > 0` after a run
- `mesh/report.json` shows the number of emitted files equal to the number
  of specs that pass the gate
- For each entry in `report["errors"]`, re-running `_gate` on that spec's
  JSON returns the same reason string

## Verification
    python mesh/mesh.py
    python -c "import json; r=json.load(open('mesh/report.json')); \
               assert r['skipped_invalid'] > 0; print(r['emitted'], r['skipped_invalid'])"

## Current state
Not done. The `_gate` function was defined but never inserted into the loop.
`mesh/report.json` still shows `skipped_invalid: 0`.

## Status
state: partial
evidence-file: mesh/mesh.py
