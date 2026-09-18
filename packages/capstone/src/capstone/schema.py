import json
from pathlib import Path
from . import (INSTITUTE_ARCHETYPES, JURISDICTIONS, PLANES, SCOPES,
               make_institute, make_capstone_record, make_interop,
               validate_capstone)


def build_all(dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for name, data in [
        ("institute_archetypes.json", INSTITUTE_ARCHETYPES),
        ("jurisdictions.json", JURISDICTIONS),
        ("planes.json", PLANES),
        ("scopes.json", SCOPES),
    ]:
        p = dest / name
        p.write_text(json.dumps(data, indent=2))
        written.append(str(p))
    sample_inst = make_institute(
        "INST-EXAMPLE", "university", "EU",
        [{"name": "Example Rector", "role": "authority"}]
    )
    sample_cap = make_capstone_record(
        "INST-EXAMPLE", "knowledge", "institutional", "INST-EXAMPLE"
    )
    sample_interop = make_interop(
        "INST-EXAMPLE",
        emits=["knowledge", "evidence"],
        consumes=["intent"],
        refuses=["execution"],
    )
    p = dest / "example_institute.json"
    p.write_text(json.dumps(sample_inst, indent=2))
    written.append(str(p))
    p = dest / "example_capstone_record.json"
    p.write_text(json.dumps(sample_cap, indent=2))
    written.append(str(p))
    p = dest / "example_interop.json"
    p.write_text(json.dumps(sample_interop, indent=2))
    written.append(str(p))
    errs = validate_capstone([sample_cap])
    p = dest / "example_validation.json"
    p.write_text(json.dumps({"errors": errs}, indent=2))
    written.append(str(p))
    return written
