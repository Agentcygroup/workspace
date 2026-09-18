# Agentcy Workspace

Engineering workspace for Agentcy Group.

## Packages

| Package | Description | Owner |
|---|---|---|
| agentcy-core | core primitives | @Agentcygroup |
| agentcy-cli  | CLI entry point | @Agentcygroup |

## Install

    python -m venv .venv
    . .venv/bin/activate
    pip install -e packages/core -e packages/cli

## Test

    python -m pytest -q

## Use

    agentcy hash hello

## Governance

See GOVERNANCE.md and SECURITY.md.
