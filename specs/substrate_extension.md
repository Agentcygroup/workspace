# Specification: Extensible Substrate Probe Registry

## Artifact
A public function `register_probe(name: str, probe: Callable[[], ProbeResult])`
that adds a probe to `PROBES` at runtime. Substrates registered through
this function are indistinguishable from built-in ones.

## Interface
    from buildability.substrate import register_probe, ProbeResult

    def probe_my_platform() -> ProbeResult:
        # inspect environment, return availability
        return ProbeResult(True, False, "my platform detected")

    register_probe("my-platform", probe_my_platform)
    # subsequent calls to probe("my-platform") use this

## Evidence
- A test registers a probe and asserts `probe("my-platform").available`
- A test registers a probe that returns unknown and asserts the flag path
  fires
- After registration, a spec with `substrate: "my-platform"` reaches G3
  in `evaluate()`

## Verification
    python -m pytest packages/buildability/tests/test_substrate_registry.py -q

## Current state
Partial. `PROBES` is a hardcoded dict with no registration function.
