# Specification: Spec Versioning

## Artifact
A `version` field on every spec, plus a registry mapping spec versions to
the schema they conform to. Loading a spec with an unsupported version
fails with a specific error.

## Interface
    {
      "kind_id": "UCI-CMS",
      "version": "v1",
      ...rest
    }

## Evidence
- `python -m buildability.classify --version-check mesh/specs_uci` passes
  for all v1 specs
- A spec labeled `v0` is rejected with "unsupported version"
- A spec with no version field is rejected with "version required"

## Verification
    python -m pytest packages/buildability/tests/test_versioning.py -q

## Current state
Not done. Specs have no version field.

## Status
state: not-done
