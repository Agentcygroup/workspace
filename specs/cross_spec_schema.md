# Specification: Cross-Spec Schema

## Artifact
A field on `Interface` called `consumes`, listing interface names this
spec depends on. `evaluate_many` uses it to check that every consumed
interface has exactly one producer.

## Interface
    interface = Interface(
        name="orders.create",
        schema="openapi",
        protocol="http",
        version="v1",
        failure_semantics="5xx",
        consumes=["auth.verify"],
    )

## Evidence
- A spec consuming an interface no other spec produces fails composition
  with a specific mismatch entry
- A spec consuming an interface produced by exactly one other spec passes
  composition
- Two specs consuming the same interface from the same producer pass
- Circular consumption is detected and reported

## Verification
    python -m pytest packages/buildability/tests/test_cross_spec.py -q

## Current state
Not done. Interfaces have no `consumes` field.
