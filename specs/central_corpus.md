# Specification: Central-Claim Positive Corpus

## Artifact
A corpus of at least 10 specs that pass all gates and build into running
systems, plus at least 10 specs that fail at least one gate and refuse to
build. Every spec has an outcome record naming its regime and its build
result.

## Interface
    experiments/corpus/
      positive/        # specs that should build
      negative/        # specs that should refuse
      outcomes.json    # label per spec

## Evidence
- `outcomes.json` has >= 10 entries with `regime == "BUILDABLE"` and
  `build_succeeded: true`
- `outcomes.json` has >= 10 entries with `build_succeeded: false` and
  a non-BUILDABLE regime
- `test_central_claim_g1_passing_builds` passes over the positive corpus
- `test_central_claim_g1_failing_fails` passes over the negative corpus

## Verification
    python -m pytest packages/buildability/tests/test_central_corpus.py -q

## Current state
Partial. The corpus has one positive case and two negatives. Not enough
to establish the claim statistically.
