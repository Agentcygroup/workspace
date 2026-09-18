TERMS = [
    {"id":"T-CON-001","label":"Record","primitive_id":"CON-ENT-001","source":"ISO-1087","status":"citable"},
    {"id":"T-CON-002","label":"Class","primitive_id":"CON-ENT-001","source":"W3C-OWL","status":"citable"},
    {"id":"T-CON-003","label":"Property","primitive_id":"CON-FIE-001","source":"W3C-RDF","status":"citable"},
    {"id":"T-CON-004","label":"Relationship","primitive_id":"CON-REL-001","source":"W3C-OWL","status":"citable"},
    {"id":"T-CON-005","label":"Schema","primitive_id":"CON-SCH-001","source":"ISO-11179","status":"citable"},
    {"id":"T-CON-006","label":"Index","primitive_id":"CON-IND-001","source":"ISO-25964","status":"citable"},
    {"id":"T-CON-007","label":"Taxonomy","primitive_id":"CON-SCH-002","source":"ISO-25964","status":"citable"},
    {"id":"T-CON-008","label":"Ontology","primitive_id":"CON-SCH-003","source":"W3C-OWL","status":"citable"},
    {"id":"T-GOV-001","label":"Permission","primitive_id":"GOV-PER-001","source":"NIST-800-162","status":"citable"},
    {"id":"T-GOV-002","label":"Prohibition","primitive_id":"GOV-PRO-001","source":"NIST-800-162","status":"citable"},
    {"id":"T-GOV-003","label":"Obligation","primitive_id":"GOV-OBL-001","source":"NIST-800-53","status":"citable"},
    {"id":"T-GOV-004","label":"Delegation","primitive_id":"GOV-DEL-001","source":"NIST-800-162","status":"citable"},
    {"id":"T-GOV-005","label":"Scope","primitive_id":"GOV-SCO-001","source":"ISO-27001","status":"citable"},
    {"id":"T-GOV-006","label":"Authority","primitive_id":"GOV-DEL-002","source":"NIST-800-162","status":"citable"},
    {"id":"T-GOV-007","label":"Responsibility","primitive_id":"GOV-OBL-002","source":"ISO-27001","status":"citable"},
    {"id":"T-GOV-008","label":"Accountability","primitive_id":"GOV-OBL-003","source":"ISO-27001","status":"citable"},
    {"id":"T-EXE-001","label":"Task","primitive_id":"EXE-TAS-001","source":"ISO-9001","status":"citable"},
    {"id":"T-EXE-002","label":"Workflow","primitive_id":"EXE-WOR-001","source":"WfMC-Reference","status":"citable"},
    {"id":"T-EXE-003","label":"Schedule","primitive_id":"EXE-SCH-001","source":"ISO-8601","status":"citable"},
    {"id":"T-EXE-004","label":"Resource","primitive_id":"EXE-RES-001","source":"ISO-9001","status":"citable"},
    {"id":"T-EXE-005","label":"Checkpoint","primitive_id":"EXE-CHE-001","source":"ISO-27001","status":"citable"},
    {"id":"T-EXE-006","label":"Job","primitive_id":"EXE-TAS-002","source":"emergent","status":"emergent"},
    {"id":"T-EXE-007","label":"Pipeline","primitive_id":"EXE-WOR-002","source":"emergent","status":"emergent"},
    {"id":"T-VER-001","label":"Assertion","primitive_id":"VER-ASS-001","source":"ISO-15026","status":"citable"},
    {"id":"T-VER-002","label":"Test","primitive_id":"VER-TES-001","source":"ISO-29119","status":"citable"},
    {"id":"T-VER-003","label":"Attestation","primitive_id":"VER-ATT-001","source":"in-toto","status":"citable"},
    {"id":"T-VER-004","label":"Proof","primitive_id":"VER-PRO-001","source":"ISO-15026","status":"citable"},
    {"id":"T-VER-005","label":"Coverage","primitive_id":"VER-COV-001","source":"ISO-29119","status":"citable"},
    {"id":"T-VER-006","label":"Signature","primitive_id":"VER-ATT-002","source":"IETF-RFC-8446","status":"citable"},
    {"id":"T-ADA-001","label":"Rule","primitive_id":"ADA-RUL-001","source":"NIST-800-53","status":"citable"},
    {"id":"T-ADA-002","label":"Policy","primitive_id":"ADA-POL-001","source":"ISO-27001","status":"citable"},
    {"id":"T-ADA-003","label":"Rewrite","primitive_id":"ADA-REW-001","source":"emergent","status":"emergent"},
    {"id":"T-ADA-004","label":"Migration","primitive_id":"ADA-MIG-001","source":"ISO-14764","status":"citable"},
    {"id":"T-ADA-005","label":"Retirement","primitive_id":"ADA-RET-001","source":"ISO-14764","status":"citable"},
    {"id":"T-OBS-001","label":"Event","primitive_id":"OBS-EVE-001","source":"W3C-PROV","status":"citable"},
    {"id":"T-OBS-002","label":"Metric","primitive_id":"OBS-MET-001","source":"ISO-80000","status":"citable"},
    {"id":"T-OBS-003","label":"Trace","primitive_id":"OBS-TRA-001","source":"W3C-PROV","status":"citable"},
    {"id":"T-OBS-004","label":"Log","primitive_id":"OBS-LOG-001","source":"ISO-27001","status":"citable"},
    {"id":"T-OBS-005","label":"Audit","primitive_id":"OBS-AUD-001","source":"ISO-27001","status":"citable"},
    {"id":"T-OBS-006","label":"Provenance","primitive_id":"OBS-EVE-002","source":"W3C-PROV","status":"citable"},
]

_BY_ID = {t["id"]: t for t in TERMS}

def get_term(tid):
    return _BY_ID.get(tid)

def terms_by_source(src):
    return [t for t in TERMS if t["source"] == src]

def terms_by_atom(aid):
    return [t for t in TERMS if t["primitive_id"] == aid]

def sources():
    return sorted({t["source"] for t in TERMS})
