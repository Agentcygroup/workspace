REFUSALS = {
    "compliance_without_signature": "no artifact may claim compliance without a signature from an accredited assessor",
    "agi_without_test": "no artifact may claim AGI or a benchmark pass without a supporting test",
    "transport_without_invocation": "no artifact may claim transport across substrates that were not invoked",
    "completion_of_open_domain": "no artifact may claim completion, exhaustiveness, or universality of an open domain",
    "promise_document": "no bridge or framework document may promise that the above will be true",
    "package_name_overreach": "no package name may imply more than its contents deliver",
}

def refuses(claim_kind):
    return claim_kind in REFUSALS

def refusal_text(claim_kind):
    return REFUSALS.get(claim_kind, "")
