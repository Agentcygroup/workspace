from .verbs import VERBS, KINDS

def _mk(verb, kind, n, accepts=None, emits=None, terms=None, prov=None):
    prefix = verb[:3].upper()
    kid = kind[:3].upper()
    return {
        "id": f"{prefix}-{kid}-{n:03d}",
        "verb": verb,
        "kind": kind,
        "accepts": accepts or [],
        "emits": emits or [],
        "industry_terms": terms or [],
        "provenance": prov or ["primitive:builtin"],
    }

def _build():
    out = []
    n = {v: {} for v in VERBS}
    for verb in VERBS:
        for kind in KINDS[verb]:
            n[verb][kind] = 0
            for i in range(1, 4):
                n[verb][kind] = i
                out.append(_mk(verb, kind, i))
    return out

ATOMS = _build()
_BY_ID = {a["id"]: a for a in ATOMS}

def get_atom(aid):
    return _BY_ID.get(aid)

def atoms_by_verb(v):
    return [a for a in ATOMS if a["verb"] == v]

def atoms_by_kind(v, k):
    return [a for a in ATOMS if a["verb"] == v and a["kind"] == k]

def atom_ids():
    return [a["id"] for a in ATOMS]
