VERBS = ["construct", "govern", "execute", "verify", "adapt", "observe"]

KINDS = {
    "construct": ["entity", "relation", "field", "schema", "index"],
    "govern": ["permission", "prohibition", "obligation", "delegation", "scope"],
    "execute": ["task", "workflow", "schedule", "resource", "checkpoint"],
    "verify": ["assertion", "test", "attestation", "proof", "coverage"],
    "adapt": ["rule", "policy", "rewrite", "migration", "retirement"],
    "observe": ["event", "metric", "trace", "log", "audit"],
}

def is_verb(v):
    return v in VERBS

def is_kind(v, k):
    return k in KINDS.get(v, [])
