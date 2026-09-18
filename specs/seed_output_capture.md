# Specification: Seed Output Capture

## Artifact
Every invocation of `seeds.py` writes its stdout to
`docs/mermaids/<query>.stdout.txt` alongside the `.mmd` file, so the exact
input that produced each diagram is preserved.

## Interface
    python packages/seeds/seeds.py security --write docs/mermaids/
    # writes both docs/mermaids/security.mmd and docs/mermaids/security.stdout.txt

## Evidence
- For every `.mmd` file, a matching `.stdout.txt` exists
- The stdout file contains the field size line and the query name
- Re-running the command overwrites both files

## Verification
    for m in docs/mermaids/*.mmd; do
      test -f "${m%.mmd}.stdout.txt" || echo "missing: $m"
    done

## Current state
Not done. Only the `.mmd` files are written.
