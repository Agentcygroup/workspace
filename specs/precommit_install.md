# Specification: Pre-Commit Hook Installation

## Artifact
`.pre-commit-config.yaml` exists AND `pre-commit install` has been run in
the repo, so the hooks fire on commit.

## Interface
    pre-commit install
    # .git/hooks/pre-commit exists and is executable

## Evidence
- `.git/hooks/pre-commit` exists
- Committing a file with trailing whitespace fails
- Committing a file with two trailing newlines fails

## Verification
    test -x .git/hooks/pre-commit && echo "installed"

## Current state
Partial. The config file exists; the hook was never installed.
