from .gaps import IMPLEMENTED_MOATS, GAP_MOATS, gap_count, implemented_count
from .articles import ARTICLES
from .refusals import REFUSALS

def conformance_report():
    return {
        "standard_version": "1.0.0",
        "articles": len(ARTICLES),
        "refusals": len(REFUSALS),
        "moats_total": len(IMPLEMENTED_MOATS) + gap_count(),
        "moats_implemented": implemented_count(),
        "moats_gap": gap_count(),
        "gap_names": GAP_MOATS,
        "scoped_completion": False,
        "unscoped_completion": "undefined",
    }
