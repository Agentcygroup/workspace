# Specification: Model Binding in Production Paths

## Artifact
Every spec in `mesh/specs_uci` and `mesh/specs_expanded` with a
`"model"` field is bound to that model at `evaluate()` time, and G3/G4/G5
run for that spec using the model's solver/prover/resolver.

## Interface
    from buildability import spec_from_file, evaluate

    spec = spec_from_file("mesh/specs_uci/UCI-CMS.json")
    verdict = evaluate(spec)
    assert verdict.regime in ("BUILDABLE",)  # model was consulted
    assert any(r.gate.value == "G3" for r in verdict.results)

## Evidence
- Every UCI spec's verdict has a G3 result that says "candidate produced"
- Every UCI spec's verdict has a G4 result that says "prover falsifiable"
- Every UCI spec's verdict has a G5 result that says "resolver total"
- Removing the `model` field from a spec drops its regime to CONSTRUCTION

## Verification
    python packages/buildability/classify.py mesh/specs_uci --verbose | grep G3

## Current state
Partial. `_bind_model` exists but is not invoked from `evaluate()` for
any spec except through test cases.

## Status
state: partial
