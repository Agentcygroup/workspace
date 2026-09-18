

def order_by_severity(spec):
    """Order open gaps: blocking first, nice-to-have last."""
    def score(g):
        q = g.question.lower()
        if "blocks" in q or "critical" in q:
            return 0
        if "may" in q or "nice" in q:
            return 2
        return 1
    return tuple(sorted(spec.open_gaps(), key=score))
