# Decisions

Each file in this directory is a decision that only a human can make.
The attest tool reads them and generates the corresponding standards
artifact. If a decision file is absent, the tool refuses to generate
that artifact and records the reason.

Four decisions are required for full standards conformance:

  security.json         -> who attacks this, what's the worst outcome
  ai_rmf.json           -> is this an AI system under EU AI Act / NIST AI RMF
  sqa.json              -> who is responsible, what's the review cadence
  quality_model.json    -> what is the framework's declared purpose

The files are read-only to the tool. Change a file, re-run the tool,
the artifact changes. The tool never invents a decision.
