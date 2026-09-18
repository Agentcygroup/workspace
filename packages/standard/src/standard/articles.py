ARTICLES = {
    1: "Deliverable artifacts must exist, execute, and state scope.",
    2: "Build determinism is required. Content hashes are required. Compile-time applies only to compiled languages.",
    3: "Generated code may omit comments. Hand-authored code carries comments. Blank lines are permitted. Hashes are not removed.",
    4: "Autonomy requires running components. Scaffolds are not autonomy.",
    5: "Generators may emit files. Emitted names may not exceed emitted behavior.",
    6: "Only reproducible build with signed SBOM is implemented end to end.",
    7: "Delivery is a signed-off commit. Completion claims require tests.",
    8: "Conformance is tested. Non-conformance names the article and the file.",
    9: "Refusals: no unsigned compliance, no AGI claim, no uninvoked transport, no open-domain completion, no promise document, no overreaching package name.",
    10: "This standard is versioned. Version 1.0.0 is the first.",
}

def get_article(n):
    return ARTICLES.get(n)
