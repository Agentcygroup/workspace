# Specification: OmniTech as Software

## Artifact
A single executable that instantiates the tools named in the OmniTech
graph as runnable services, each with a declared interface, and a
super-node that dispatches requests.

## Interface
    python -m omnitech serve --port 8080
    # exposes a graph-derived dispatch endpoint:
    curl localhost:8080/dispatch -d '{"task": "generate_image", "input": "..."}'

## Evidence
- `python -m omnitech serve` starts and responds on the declared port
- Each named tool is instantiated and reachable
- The super-node dispatches a request and records the outcome

## Verification
    python -m pytest packages/omnitech/tests/test_omnitech.py -q

## Current state
Not done. OmniTech exists as a parsed graph of a conversation about it,
not as a running system.

## Status
state: not-done
