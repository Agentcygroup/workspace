# Capstone over institutes — research agenda

A capstone over "all institutes" would need to federate universities,
research labs, standards bodies, certification bodies, regulators,
hospitals, schools, libraries, archives, courts, defense agencies,
intelligence agencies, public health agencies, central banks,
statistics offices, space agencies, metrology institutes, consortia,
industry alliances, open source foundations, professional societies,
charities, cooperatives, and municipalities.

Each of those is a legal entity in one or more jurisdictions with an
authority chain, a mandate, and a body of evidence it accepts or
refuses. Federating them is not a document. It is a program.

## What already exists for parts of this

- **Identity and credentials** — W3C DID Core, W3C VC Data Model
- **Measurement** — BIPM, ISO 80000, ISO/IEC 17025
- **Information security** — ISO/IEC 27001, NIST SP 800-53, NIST CSF
- **Assurance cases** — ISO/IEC 15026, GSN (Goal Structuring Notation)
- **Evaluation criteria** — ISO/IEC 15408 (Common Criteria)
- **Education and curriculum** — ACM/IEEE CS2023, SFIA 9
- **Research infrastructure** — InCommon, eduGAIN, REFEDS
- **Trust frameworks** — Kantara, OIX, OpenID Foundation
- **Cross-border data** — GDPR adequacy decisions, CBPR, Privacy Shield successors

Each of these solves a piece. None solves federation across all of them.

## What is missing

1. **A common institute identity** that is legible across jurisdictions
   without asserting recognition.
2. **A plane-governance algebra** that says which institute governs
   which plane at which scope, with no duplicate governors.
3. **An evidence transport** that preserves provenance and signature
   across jurisdictional boundaries without collapsing into one
   authority's audit trail.
4. **A refusal protocol** — institutes must be able to consume nothing,
   emit nothing, and still participate in the federation as observers.
5. **A human authority layer** — every capstone claim signed by a named
   human at that institute with a real key, in a real jurisdiction, at
   a real time.
6. **A jurisdiction check** — every cross-institute transport runs a
   procedural check; no transport asserts recognition.

## What this workspace currently implements

- `agentcy-capstone` — institute archetypes, jurisdictions, planes,
  scopes, and a validator that enforces "one governor per (plane, scope)"
- `agentcy-capstone-flow` — a synthetic four-step flow across three
  institute archetypes, each step carried in a kernel envelope with
  provenance.
- `agentcy-kernel` — operators, axioms, mappings, sandbox, four domain
  adapters (physics, biology, medicine, enterprise).

## What this workspace does not implement

- No real institute is enrolled.
- No real human has signed anything.
- No jurisdiction has recognized anything.
- The flow is synthetic and says so.
- The atlas from the DEV AGENT SKILL ATLAS file is not implemented
  end to end; it is a shape that the capstone packages can grow into.

## Honest scope

This capstone is a substrate. It is not a claim. Adding a real
institute requires:

- a signed institute record (DID or equivalent)
- a named human in its authority chain
- a jurisdiction declaration
- a signed capstone record for each plane it governs
- an interop record declaring emits, consumes, refuses
- a jurisdiction check record
- an audit event in `audit/hil_audit.jsonl`

None of those are automatic. All are checkable. That is the shape.
