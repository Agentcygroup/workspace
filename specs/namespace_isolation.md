# Specification: Namespace Isolation

## Artifact
A registry file at the repository root that maps every top-level Python
package name to the directory that provides it. A pre-commit check fails
if two directories claim the same top-level name.

## Interface
    # namespace.toml
    [packages]
    buildability = "packages/buildability/src/buildability"
    attest = "packages/attest/src/attest"
    ...

## Evidence
- `python -m namespace_check` exits 0 on the current repo
- Introducing a second `attest` package causes it to exit non-zero
- The error message names both conflicting directories

## Verification
    python -m namespace_check

## Current state
Not done. The `attest` collision was diagnosed at the pytest level but
no registry prevents the class of bug.
