# distributed_coordination

## Purpose
Two autonomy decisions can be coordinated as a single transaction.

## Interface
coordinate.two_phase_commit(a, b, ctx_a, ctx_b, contract) -> CoordinationResult. Commit only if both allow.

state: done
evidence-file: packages/autonomy/src/autonomy/coordinate.py
