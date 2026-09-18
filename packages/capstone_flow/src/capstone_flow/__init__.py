"""Capstone coordination flow across three institute archetypes.

Synthetic end-to-end: a hospital intent is cited by a standards body,
implemented at a university, evidenced back through the chain, each
step mapped through the kernel envelope.
"""
__version__ = "0.1.0"
from kernel.envelope import make_envelope, verify_envelope
from kernel.mappings import MAPPINGS


def flow(hospital_id, standards_body_id, university_id):
    steps = []
    # Step 1: hospital emits intent
    intent = make_envelope(
        env_id="FLOW-INTENT",
        domain="medicine",
        native_schema="intent.v1",
        payload={"intent": "reduce_medication_errors", "units": "count"},
        units={"errors": "count"},
        preserved=["provenance", "source_hash"],
        provenance=[hospital_id],
    )
    steps.append({"step": 1, "actor": hospital_id, "envelope": intent.to_dict()})

    # Step 2: standards body cites the intent as a requirement
    cite = make_envelope(
        env_id="FLOW-CITE",
        domain="enterprise",
        native_schema="citation.v1",
        payload={"cites": intent.id, "requirement_id": "REQ-001"},
        units={},
        preserved=["provenance", "source_hash"],
        provenance=[standards_body_id, "cites:" + intent.id],
    )
    steps.append({"step": 2, "actor": standards_body_id, "envelope": cite.to_dict()})

    # Step 3: university implements
    impl = make_envelope(
        env_id="FLOW-IMPL",
        domain="enterprise",
        native_schema="implementation.v1",
        payload={"requirement_id": "REQ-001", "implementation_id": "IMPL-001"},
        units={},
        preserved=["provenance", "source_hash"],
        provenance=[university_id, "implements:" + cite.id],
    )
    steps.append({"step": 3, "actor": university_id, "envelope": impl.to_dict()})

    # Step 4: evidence back to the hospital
    ev = make_envelope(
        env_id="FLOW-EVIDENCE",
        domain="medicine",
        native_schema="evidence.v1",
        payload={"implementation_id": "IMPL-001", "evidence": "IMPL-001 test log"},
        units={},
        preserved=["provenance", "source_hash"],
        provenance=[university_id, "evidence-for:" + impl.id],
    )
    steps.append({"step": 4, "actor": university_id, "envelope": ev.to_dict()})

    return {
        "flow_id": "FLOW-001",
        "participants": [hospital_id, standards_body_id, university_id],
        "steps": steps,
        "non_implication": (
            "This flow is synthetic. No hospital, standards body, or university "
            "has participated. No jurisdiction has recognized anything."
        ),
    }


def verify_flow(f):
    errs = []
    for s in f["steps"]:
        env = s["envelope"]
        if env["schema_version"] != "0.1.0":
            errs.append("step " + str(s["step"]) + " wrong schema version")
        if not env.get("provenance"):
            errs.append("step " + str(s["step"]) + " missing provenance")
        if env.get("domain") == "":
            errs.append("step " + str(s["step"]) + " empty domain")
    return errs


def build_all(dest):
    import json
    from pathlib import Path
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    f = flow("INST-HOSPITAL", "INST-STANDARDS", "INST-UNIVERSITY")
    p = dest / "flow.json"
    p.write_text(json.dumps(f, indent=2))
    p2 = dest / "flow_validation.json"
    p2.write_text(json.dumps({"errors": verify_flow(f)}, indent=2))
    return [str(p), str(p2)]
