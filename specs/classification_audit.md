# Specification: Classification Audit Log

## Artifact
Every call to `evaluate()` appends an entry to
`standards/classification_log.jsonl` with the spec name, regime, timestamp,
and the git commit at time of classification.

## Interface
    {"spec": "UCI-CMS", "regime": "BUILDABLE", "at": "...", "commit": "..."}

## Evidence
- After running `python -m buildability.classify mesh/specs_uci`, the log
  has 40 entries
- Entries are append-only; re-running adds, never removes
- The commit field matches `git rev-parse HEAD` at classification time

## Verification
    wc -l standards/classification_log.jsonl
    tail -1 standards/classification_log.jsonl

## Current state
Not done. Classification is stateless.

## Status
state: not-done
