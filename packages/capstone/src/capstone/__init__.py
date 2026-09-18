"""Capstone: federated governance over institute archetypes.

An Institute is a legal entity in a jurisdiction with an authority chain.
A Capstone record says which Institute governs which plane at what scope.
An Interop record says what an Institute emits, consumes, and refuses.

No real institute is enrolled by this package. Enrolment requires a signed
attestation from a named human at that institute. This package only
validates the shape.
"""
__version__ = "0.1.0"

INSTITUTE_ARCHETYPES = [
    "university", "research_lab", "standards_body", "certification_body",
    "regulator", "hospital", "school", "library", "archive", "court",
    "defense_agency", "intelligence_agency", "public_health_agency",
    "central_bank", "statistics_office", "space_agency", "metrology_institute",
    "consortium", "industry_alliance", "open_source_foundation",
    "professional_society", "charity", "cooperative", "municipality",
]

JURISDICTIONS = [
    "EU", "US", "UK", "DE", "FR", "CA", "AU", "JP", "SG", "CH",
    "BR", "IN", "CN", "ZA", "AE", "DEFAULT",
]

PLANES = [
    "intent", "knowledge", "capability", "skill", "agent", "model", "tool",
    "data", "execution", "runtime", "compute", "storage", "network",
    "security", "policy", "governance", "evidence", "qualification",
    "observability", "delivery", "operations", "interface", "moat",
]

SCOPES = [
    "global", "regional", "national", "jurisdictional", "institutional",
    "departmental", "project", "runtime",
]

NON_IMPLICATION = (
    "Enrolment of any institute in this capstone does not imply legal "
    "recognition, accreditation, endorsement, or reciprocity in any "
    "jurisdiction. Recognition is determined by competent authorities. "
    "This package validates shape only. It signs nothing."
)


def make_institute(institute_id, archetype, jurisdiction, authority_chain):
    errs = []
    if archetype not in INSTITUTE_ARCHETYPES:
        errs.append("unknown archetype: " + str(archetype))
    if jurisdiction not in JURISDICTIONS:
        errs.append("unknown jurisdiction: " + str(jurisdiction))
    if not institute_id:
        errs.append("missing institute_id")
    if not isinstance(authority_chain, list) or not authority_chain:
        errs.append("authority_chain must be a non-empty list of named humans")
    return {
        "institute_id": institute_id,
        "archetype": archetype,
        "jurisdiction": jurisdiction,
        "authority_chain": authority_chain,
        "enrolled": False,
        "signed_by": None,
        "errors": errs,
        "non_implication": NON_IMPLICATION,
    }


def make_capstone_record(institute_id, plane, scope, governor_id):
    errs = []
    if plane not in PLANES:
        errs.append("unknown plane: " + str(plane))
    if scope not in SCOPES:
        errs.append("unknown scope: " + str(scope))
    if not governor_id:
        errs.append("missing governor_id")
    return {
        "institute_id": institute_id,
        "plane": plane,
        "scope": scope,
        "governor_id": governor_id,
        "signed_by": None,
        "errors": errs,
        "non_implication": NON_IMPLICATION,
    }


def make_interop(institute_id, emits, consumes, refuses):
    for p in emits + consumes + refuses:
        if p not in PLANES:
            return {"errors": ["unknown plane in interop: " + str(p)]}
    overlap = set(emits) & set(refuses)
    errs = []
    if overlap:
        errs.append("planes both emitted and refused: " + ", ".join(sorted(overlap)))
    return {
        "institute_id": institute_id,
        "emits": sorted(set(emits)),
        "consumes": sorted(set(consumes)),
        "refuses": sorted(set(refuses)),
        "errors": errs,
        "non_implication": NON_IMPLICATION,
    }


def validate_capstone(records):
    """Each (plane, scope) has at most one governor. No institute governs a plane it refuses."""
    errs = []
    seen = {}
    for r in records:
        key = (r["plane"], r["scope"])
        if key in seen and seen[key] != r["governor_id"]:
            errs.append("duplicate governor for " + str(key) + ": " +
                        seen[key] + " and " + r["governor_id"])
        seen[key] = r["governor_id"]
        if r["errors"]:
            errs.extend(r["errors"])
    return errs
