from .terms import TERMS
from primitives import get_atom

def validate_term(t):
    errs = []
    for k in ["id","label","primitive_id","source","status"]:
        if k not in t:
            errs.append("missing " + k)
    if t.get("status") not in ("citable","emergent"):
        errs.append("bad status: " + str(t.get("status")))
    if t.get("primitive_id") and get_atom(t["primitive_id"]) is None:
        errs.append("unknown primitive: " + t["primitive_id"])
    return errs

def validate_all():
    errs = []
    ids = set()
    for t in TERMS:
        if t["id"] in ids:
            errs.append("duplicate term: " + t["id"])
        ids.add(t["id"])
        for e in validate_term(t):
            errs.append(t["id"] + ": " + e)
    return errs
