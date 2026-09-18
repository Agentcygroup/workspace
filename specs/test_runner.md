# Specification: Batched Test Attester

## Artifact
The gap tool's `_attest_test` runs pytest once per test, spawning 412
subprocesses for 412 test claims. The spec requires a batched runner that
invokes pytest once per source file and reads the per-test results from
the report.

## Interface
    def attest_tests_batch(root: Path, claims: list[Claim]) -> dict[str, bool]:
        # groups claims by source file
        # runs pytest --json-report per file
        # returns {test_name: passed}

## Evidence
- `python packages/gaps/gaps.py` completes in under 30 seconds
- The number of pytest subprocesses equals the number of distinct source
  files, not the number of test claims
- The attested/unattested counts are identical to the per-test runner

## Verification
    time python packages/gaps/gaps.py
    # compare attested count before and after batching

## Current state
Not done. The attester runs one subprocess per test.

## Status
state: partial
evidence-file: packages/gaps/src/gaps/attest.py
