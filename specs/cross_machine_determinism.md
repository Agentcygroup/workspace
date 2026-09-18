# Specification: Cross-Machine Determinism

## Artifact
The seed graph produced by `python packages/seeds/seeds.py --stats` is
byte-identical when run on two different machines with the same Python
major.minor version and the same git commit checked out.

## Interface
    # on machine A:
    python packages/seeds/seeds.py --stats > /tmp/stats_a.txt
    # on machine B:
    python packages/seeds/seeds.py --stats > /tmp/stats_b.txt
    # assert equal

## Evidence
- `packages/seeds/tests/test_seed_determinism.py` runs the tool twice on
  one machine and passes
- The same test, run in CI on a second machine, passes
- The diff between the two stats files is empty

## Verification
    # in CI, on two runners with the same commit:
    diff stats_a.txt stats_b.txt && echo DETERMINISTIC

## Current state
Partial. The test only runs twice on one machine. No cross-machine check.

## Status
state: partial
evidence-file: packages/seeds/tests/test_seed_determinism.py
