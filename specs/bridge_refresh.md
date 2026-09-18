# Specification: Live Bridge Report

## Artifact
`bridge/report.json` is regenerated on demand and its content matches the
current state of the repository. Stale content is detectable.

## Interface
    python -m bridge.refresh  # regenerates bridge/report.json
    python -m bridge.diff     # compares to a baseline

## Evidence
- After `python -m bridge.refresh`, every section's count matches a fresh
  computation
- Running `bridge.diff` immediately after `bridge.refresh` reports no
  differences
- The file's mtime updates on each refresh

## Verification
    python -m bridge.refresh
    python -m bridge.diff | grep -c DIFF && echo "stale"

## Current state
Partial. The report is generated once and not refreshed.

## Status
state: partial
