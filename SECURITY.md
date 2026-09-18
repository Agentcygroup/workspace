# Security

## Reporting

Report vulnerabilities to security@agentcygroup.example.

## Posture

- Every release produces an SBOM (CycloneDX JSON).
- Every release artifact is SHA-256 hashed and recorded in the manifest.
- Signing keys are managed out of band and are never committed.

## Scope at v0.1.0

Two packages: agentcy-core (pure Python, no I/O), agentcy-cli (thin CLI over core).
Neither parses untrusted input. Neither opens sockets.
