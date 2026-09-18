# spec_identity

## Purpose
Compute a content hash for a spec so two specs can be compared by identity, not by name.

## Interface
loader.spec_identity(spec: Spec) -> str. SHA-256 over canonical JSON of components, interfaces, invariants, substrate.

state: done
evidence-file: packages/buildability/src/buildability/loader.py
