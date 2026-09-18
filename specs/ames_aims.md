# Specification: AMES Model

## Artifact
A module with four functions `architecture`, `modeling`, `evaluation`,
`systematic_integration`, each taking a mission description and returning
a structured output. A top-level `ames(mission) -> dict` composes them.

## Interface
    from ames import ames

    result = ames({"mission": "space robotics"})
    assert set(result) == {"architecture", "modeling", "evaluation", "integration"}

## Evidence
- Each of the four functions returns a non-empty dict for a valid mission
- `ames` chains them so that the output of one is the input of the next
- The composition is idempotent: `ames(ames(m)) == ames(m)` for the top-
  level fields

## Verification
    python -m pytest packages/ames/tests/test_ames.py -q

## Current state
Not done. AMES exists only as prose describing what it would do.

## Status
state: not-done
