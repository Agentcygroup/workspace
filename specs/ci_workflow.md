# Specification: CI Workflow

## Artifact
A `.github/workflows/verify.yml` that on every push runs:

1. `python -m pytest packages/buildability/tests -q`
2. `python packages/attest/standards.py` and asserts `omitted_or_error: []`
3. `python packages/seeds/seeds.py --stats` and asserts node count matches
4. `python packages/gaps/gaps.py --diff` and asserts `new_unattested: []`

## Interface
On failure, the workflow exits non-zero and the diff is posted to the
workflow log.

## Evidence
- `.github/workflows/verify.yml` exists
- A push to a branch triggers the workflow
- The workflow has been run at least once and passed

## Verification
    cat .github/workflows/verify.yml
    git log --oneline -- .github/workflows/verify.yml | head -1

## Current state
Not done. No CI configuration exists.
