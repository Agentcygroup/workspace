# Specification: Model Selection Logic

## Artifact
A function `select_model(spec: Spec) -> str` that returns the name of the
model best suited to the spec, or raises `NoSuitableModel` if none applies.
The selection is based on spec properties, not on arbitrary assignment.

## Interface
    from buildability import Spec, select_model

    m = select_model(spec)
    assert m in MODEL_REGISTRY

## Evidence
- A spec whose substrate is `quantum-turing` selects `quantum`
- A spec whose components are logical constraints selects `boolean` or
  `constraint`
- A spec whose components are concurrent processes selects `pi`
- A spec with no discriminating feature raises `NoSuitableModel`
- Every selection is deterministic: same spec, same model

## Verification
    python -m pytest packages/buildability/tests/test_model_selection.py -q

## Current state
Not done. Model binding is currently `spec.model or spec.substrate`, which
is a lookup, not a selection.
