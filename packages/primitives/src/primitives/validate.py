from .verbs import is_verb, is_kind
from .atoms import ATOMS, atom_ids

REQUIRED = ["id", "verb", "kind", "accepts", "emits", "industry_terms", "provenance"]

def validate_atom(a):
    errs = []
    for k in REQUIRED:
        if k not in a:
            errs.append("missing " + k)
    if not is_verb(a.get("verb", "")):
        errs.append("unknown verb: " + str(a.get("verb")))
    if not is_kind(a.get("verb", ""), a.get("kind", "")):
        errs.append("unknown kind for verb: " + str(a.get("kind")))
    if not a.get("provenance"):
        errs.append("missing provenance")
    return errs

def validate_all():
    errs = []
    ids = set()
    for a in ATOMS:
        if a["id"] in ids:
            errs.append("duplicate id: " + a["id"])
        ids.add(a["id"])
        for e in validate_atom(a):
            errs.append(a["id"] + ": " + e)
    ids_known = set(atom_ids())
    for a in ATOMS:
        for ref in a["accepts"] + a["emits"]:
            if ref not in ids_known:
                errs.append(a["id"] + ": dangling reference " + ref)
    return errs
