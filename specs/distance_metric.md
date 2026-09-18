# Specification: Distance Metric Between Specs

## Artifact
A function `spec_distance(a: Spec, b: Spec) -> float` that returns a
number in [0, 1]. 0 means identical, 1 means maximally different.
The metric is used to rank partial specs within the same regime.

## Interface
    from buildability import Spec, spec_distance

    d = spec_distance(spec_a, spec_b)
    assert 0.0 <= d <= 1.0
    assert spec_distance(s, s) == 0.0

    # rank a corpus
    ranked = sorted(specs, key=lambda s: spec_distance(reference, s))

## Evidence
- Symmetry: `spec_distance(a, b) == spec_distance(b, a)` for all a, b
- Identity: `spec_distance(a, a) == 0.0`
- Triangle inequality: `d(a, c) <= d(a, b) + d(b, c)`
- At least one test constructs three specs at increasing distance and
  asserts the ordering

## Verification
    python -m pytest packages/buildability/tests/test_distance.py -q

## Current state
Not done. `test_fail_no_distance_metric_between_specs` documents the
absence.

## Status

state: done
evidence-file: packages/buildability/src/buildability/distance.py
