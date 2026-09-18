# Specification: Decision Revocation

## Artifact
A decision file may declare `revokes: <decision_name>` and a reason.
Artifacts generated from the revoked decision are marked superseded.

## Interface
    {
      "declared_by": "...",
      "status": "accepted",
      "revokes": "security",
      "reason": "threat model changed",
      ...
    }

## Evidence
- `python packages/attest/standards.py` marks the superseded artifact in
  `INDEX.json` with `"superseded_by": "<new_decision>"`
- Both the old and new artifacts remain in `standards/` for comparison
- `--diff` shows which artifacts changed

## Verification
    python -m pytest packages/attest/tests/test_revocation.py -q

## Current state
Not done. Decisions have no revocation mechanism.

## Status
state: not-done
