# Specification: Partial Spec Diagnostics

## Artifact
A function `diagnose(spec: Spec) -> list[Diagnostic]` that returns one
entry per element that is absent or incomplete. Each entry names the
element, its state, and what would complete it.

## Interface
    from buildability import Spec, diagnose, Diagnostic

    diagnostics = diagnose(spec)
    for d in diagnostics:
        print(d.element, d.state, d.hint)
    # e.g. "interfaces" "empty" "declare at least one interface"

## Evidence
- For a spec that fails G1 on missing interfaces, `diagnose` returns one
  diagnostic with `element == "interfaces"` and `state == "empty"`
- For a spec that fails G1 on missing components, `diagnose` returns one
  diagnostic with `element == "components"`
- For a spec that passes G1, `diagnose` returns an empty list
- The count of diagnostics equals the number of failed sub-checks

## Verification
    python -m pytest packages/buildability/tests/test_diagnose.py -q

## Current state
Not done. `test_fail_no_partial_spec_handling` documents the absence.

## Status
state: not-done
