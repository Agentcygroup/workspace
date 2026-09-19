# workspace

A repository with a spec classifier, a generative pipeline, and a
declarative autonomy contract.

## What's here

- `packages/buildability/` — classifies specs into regimes (RESEARCH,
  INCOHERENT, ENGINEERING, CONSTRUCTION, VERIFICATION, ADJUDICATION,
  BUILDABLE, DIVERGENT) via a registry of gates.
- `packages/autonomy/` — evaluates proposed actions against
  `security/autonomy_contract.yaml`. Enforces scope, level, confidence,
  blast radius, and a runtime kill switch.
- `packages/gaps/` — enumerates claims and attests them.
- `packages/seeds/` — dendritic graph over the repository's contents.
- `packages/attest/` — generates standards artifacts.
- `scripts/verify.sh` — one command to run everything.
- `specs/` — 26 specifications for work not yet done.

## Install

    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.lock
    pip install -e packages/buildability -e packages/autonomy

## Verify

    ./scripts/verify.sh

Runs 11 stages. Exits non-zero on the first failure.

## The autonomy contract

`security/autonomy_contract.yaml` declares, per scope and level, which
action classes are authorized and under what conditions.

`security/KILL_SWITCH` is a file. If it exists, every action is refused.

## License

Unspecified.

## Classifier

Run `python -m buildability.classify mesh/specs_uci` to classify the UCI corpus.

## Autonomous pipe

Run `python pipe/autonomous_pipe.py` to execute the eight-stage DevSecOps pipe.

## Standards

The standards artifacts live in `standards/`, indexed at `standards/INDEX.json`.
