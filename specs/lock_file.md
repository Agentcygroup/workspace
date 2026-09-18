# Specification: Dependency Lock File

## Artifact
A `requirements.lock` file that pins the exact version of every installed
package, generated from the current virtualenv.

## Interface
    pip freeze > requirements.lock
    pip install -r requirements.lock  # reproduces environment

## Evidence
- `pip install -r requirements.lock` in a fresh venv produces an
  environment where every test passes
- The lock file is committed
- CI installs from the lock file, not from `pip install -e`

## Verification
    pip install -r requirements.lock
    python -m pytest packages/buildability/tests -q

## Current state
Not done. No lock file exists.

## Status

state: done
evidence-file: requirements.lock
