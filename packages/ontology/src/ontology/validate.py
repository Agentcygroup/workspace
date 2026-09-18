from .levels import LEVELS, KIND_INDEX, BINDS, INVARIANTS

IMPLEMENTED = {
    "REGISTRY": ["SOURCE","PUBLICATION","SNAPSHOT","VERSION","ENTRY"],
    "LEDGER": ["CLAIM","EVIDENCE","LINK","TRACEABILITY"],
    "ARTIFACT": ["DOSSIER","DECK","WORKBOOK","MANIFEST","CERTIFICATE","COVERAGE"],
}

def implementation_status():
    out = {}
    for lvl in LEVELS:
        kinds = KIND_INDEX.get(lvl, [])
        if not kinds:
            out[lvl] = {"total": 0, "implemented": 0, "gaps": []}
            continue
        impl = IMPLEMENTED.get(lvl, [])
        gaps = [k for k in kinds if k not in impl]
        out[lvl] = {"total": len(kinds), "implemented": len(impl), "gaps": gaps}
    return out

def gap_register():
    out = []
    for lvl, s in implementation_status().items():
        for k in s["gaps"]:
            out.append({"level": lvl, "kind": k, "status": "gap"})
    return out

def validate():
    errs = []
    if len(LEVELS) != 16:
        errs.append("LEVELS must be 16")
    seen = set()
    for lvl in LEVELS:
        if lvl in seen:
            errs.append("duplicate level: " + lvl)
        seen.add(lvl)
    for src, dst in BINDS:
        if src not in LEVELS:
            errs.append("bind src unknown: " + src)
        if dst not in LEVELS:
            errs.append("bind dst unknown: " + dst)
    if len(INVARIANTS) != 15:
        errs.append("INVARIANTS must be 15")
    for lvl, kinds in KIND_INDEX.items():
        if lvl not in LEVELS:
            errs.append("kind index unknown level: " + lvl)
        for k in kinds:
            if not isinstance(k, str) or not k:
                errs.append("bad kind in " + lvl)
    return errs
