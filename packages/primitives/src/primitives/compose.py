from .atoms import ATOMS, get_atom

def compose(atom_ids=None, industry_term_index=None):
    """Return a labelled graph over the selected atoms.

    atom_ids: subset of primitive ids to include. None means all.
    industry_term_index: mapping atom_id -> list of term ids. None uses the
    atom's own industry_terms field.
    """
    if atom_ids is None:
        selected = ATOMS
    else:
        selected = [get_atom(a) for a in atom_ids if get_atom(a)]
    nodes = []
    edges = []
    for a in selected:
        terms = a["industry_terms"]
        if industry_term_index and a["id"] in industry_term_index:
            terms = industry_term_index[a["id"]]
        nodes.append({
            "id": a["id"],
            "verb": a["verb"],
            "kind": a["kind"],
            "labels": terms,
        })
        for t in a["accepts"]:
            edges.append({"from": t, "to": a["id"], "rel": "accepts"})
        for t in a["emits"]:
            edges.append({"from": a["id"], "to": t, "rel": "emits"})
    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "scoped_completion": False,
        "unscoped_completion": "undefined",
    }
