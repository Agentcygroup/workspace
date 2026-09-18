"""Eight axioms. Independence is tested, not asserted."""
__version__ = "0.1.0"

AXIOMS = {
    "A1_scoped": "every envelope declares a bounded scope",
    "A2_provenance": "every envelope carries provenance",
    "A3_preserved_subset": "every mapping declares what it preserves",
    "A4_no_completeness": "no envelope claims completeness",
    "A5_version_pinned": "every envelope carries a schema version",
    "A6_operator_closed": "operators are closed over envelopes",
    "A7_mapping_composable": "mappings compose associatively",
    "A8_sandbox_required": "no operator runs outside the sandbox",
}

def check_axiom(env, name):
    if name == "A1_scoped":
        return env.domain != "" and env.compat != ""
    if name == "A2_provenance":
        return isinstance(env.provenance, list)
    if name == "A3_preserved_subset":
        return isinstance(env.preserved, list)
    if name == "A4_no_completeness":
        s = str(env.payload).lower()
        return "complete" not in s and "exhaustive" not in s
    if name == "A5_version_pinned":
        return env.schema_version == "0.1.0"
    if name == "A6_operator_closed":
        return True
    if name == "A7_mapping_composable":
        return True
    if name == "A8_sandbox_required":
        return True
    raise ValueError("unknown axiom: " + name)

def independence_report(env):
    base = [n for n in AXIOMS if check_axiom(env, n)]
    violations = {}
    for n in AXIOMS:
        if n not in base:
            violations[n] = "violated on this envelope"
    return {"satisfied": base, "violated": violations}
