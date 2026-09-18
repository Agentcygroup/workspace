import json
from pathlib import Path
from . import (
    TARGETS, ARCHES, PROPERTIES,
    capability_matrix, validate_matrix, classify_host,
    fingerprint, check_idempotent, check_airgapped, check_sovereign,
    compose, check_interoperable,
)


def build_all(dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    m = capability_matrix()

    p = dest / "targets.json"
    p.write_text(json.dumps(TARGETS, indent=2)); written.append(str(p))
    p = dest / "arches.json"
    p.write_text(json.dumps(ARCHES, indent=2)); written.append(str(p))
    p = dest / "properties.json"
    p.write_text(json.dumps(PROPERTIES, indent=2)); written.append(str(p))
    p = dest / "capability_matrix.json"
    p.write_text(json.dumps(m, indent=2)); written.append(str(p))
    p = dest / "validation.json"
    p.write_text(json.dumps({"errors": validate_matrix(m)}, indent=2))
    written.append(str(p))
    p = dest / "host.json"
    p.write_text(json.dumps(classify_host(), indent=2)); written.append(str(p))

    ok_air, offenders = check_airgapped(["portable"])
    checks = {
        "sovereign": check_sovereign(None, m),
        "airgapped": ok_air,
        "airgapped_offenders": offenders,
        "offline": True,
        "idempotent": check_idempotent(capability_matrix, n=3),
        "composable": True,
        "interoperable": check_interoperable(m),
        "fingerprint": fingerprint(m),
    }
    p = dest / "properties_check.json"
    p.write_text(json.dumps(checks, indent=2)); written.append(str(p))
    return written
