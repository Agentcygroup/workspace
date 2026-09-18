# Specification: Cross-Repo Package Installation

## Artifact
Every package under `packages/` that contains a `pyproject.toml` is
installed editable in the active virtualenv. Every package that contains
tests is importable by pytest without path manipulation.

## Interface
    pip install -e packages/<name>

    # and for the shim at packages/attest:
    # standards.py and decide.sh import from `attest` package.

## Evidence
- `pip show <name>` for every package with a pyproject.toml returns
  a populated entry, not "Package(s) not found"
- For each package, `python -c "import <name>"` exits 0
- For each test file, `pytest <file>` collects without ImportError

## Verification
    for p in packages/*/pyproject.toml; do
      pkg=$(dirname $p | xargs basename)
      pip show $pkg >/dev/null || echo "MISSING: $pkg"
    done

## Current state
Partial. `packages/complexity` was diagnosed as not installed but was not
re-installed. `packages/attest/__init__.py` exports the names the tests
need, but `decide.py` and `interview.py` are not in `__all__`.
