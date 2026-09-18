# Governance

## Roles

- Owner: @Agentcygroup — sole signer of all gates as of v0.1.0
- Maintainer: vacant
- Reviewer: vacant
- Publisher: vacant

## Gates

| Gate | Who signs | Where recorded |
|---|---|---|
| H1 registry curator    | Owner | audit/hil_audit.jsonl |
| H2 coverage reviewer   | Owner | audit/hil_audit.jsonl |
| H3 citation verifier   | Owner | audit/hil_audit.jsonl |
| H4 conformance assessor| Owner | audit/hil_audit.jsonl |
| H5 certifying officer  | Owner | audit/hil_audit.jsonl |
| H6 jurisdiction checker| Owner | audit/hil_audit.jsonl |

No signer may sign two gates on the same PU.

## Merge policy

- main is protected
- one approval required
- all CI must pass
- signed commits required

## Release cadence

- patch: as needed
- minor: monthly
- major: at breaking change
