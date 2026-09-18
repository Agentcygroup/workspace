def detect_drift(prev_policy, new_policy, samples):
    """Return list of contexts whose decision changed between two policies."""
    changed = []
    for ctx in samples:
        a = prev_policy.evaluate(ctx).effect
        b = new_policy.evaluate(ctx).effect
        if a != b:
            changed.append({"ctx": ctx, "was": a, "now": b})
    return changed
