# Kernel

The kernel is small on purpose. It defines:

- 10 semantic operators, each with a denotation and a pure implementation
- 8 axioms, each with a test that exercises it alone
- 3 cross-domain mappings, each declaring what it preserves
- 1 canonical envelope that every domain emits and consumes
- 1 sandbox that enforces signature, lint, version pin, resource limit, timeout

## What the kernel claims

- Operators are closed over envelopes.
- Mappings preserve only their declared subset.
- The sandbox refuses unknown operators and oversized payloads.
- No envelope may claim completeness (axiom A4).

## What the kernel does not claim

- It is not a universal translator.
- It is not a mathematical polyglot.
- It is not a bridge to quantum hardware.
- It does not know what a photon is, a genome is, or a ledger is.
- It does not provide native-to-legacy-to-quantum transport.

## How to extend

Add a domain adapter under `src/kernel/domains/` that emits
`make_envelope(...)`. Add a mapping under `MAPPINGS` that declares
`from`, `to`, `preserved`, `rationale`. Add a test. Push.

The core does not change. That is MP6.
