# Specification: Gap-History Generator

## Artifact
A function `close_one_gap(spec: Spec) -> Spec` that resolves exactly one
open gap, plus a loop `iterate(spec, max_iterations) -> (Spec, list[int])`
that returns the final spec and the sequence of open-gap counts.

## Interface
    from buildability import Spec, iterate

    final, history = iterate(spec, max_iterations=100)
    # history[-1] == 0 means converged
    # a non-decreasing history means divergent

## Evidence
- For a spec with N open gaps, `iterate` produces a history of length
  N+1 ending in 0
- For a spec where `close_one_gap` cannot resolve anything, `iterate`
  returns a history that plateaus and does not converge
- `_g0` fires DIVERGENT on the plateau case

## Verification
    python -m pytest packages/buildability/tests/test_gap_history.py -q

## Current state
Not done. `test_fail_divergence_requires_external_history` documents the
absence.
