from primitives import VERBS, KINDS, ATOMS, get_atom, atoms_by_verb, atoms_by_kind, validate_all, compose
from primitives.verbs import is_verb, is_kind
from primitives.atoms import atom_ids
from primitives.validate import validate_atom

def test_verbs_closed():
    assert VERBS == ["construct","govern","execute","verify","adapt","observe"]

def test_kinds_closed():
    for v in VERBS:
        assert len(KINDS[v]) == 5

def test_atoms_count():
    assert len(ATOMS) == 6 * 5 * 3

def test_atom_shape():
    a = ATOMS[0]
    for k in ["id","verb","kind","accepts","emits","industry_terms","provenance"]:
        assert k in a

def test_validate_all_clean():
    assert validate_all() == []

def test_get_atom():
    a = get_atom(ATOMS[0]["id"])
    assert a is not None
    assert a["id"] == ATOMS[0]["id"]

def test_atoms_by_verb():
    assert len(atoms_by_verb("construct")) == 15
    assert len(atoms_by_verb("govern")) == 15

def test_atoms_by_kind():
    assert len(atoms_by_kind("construct","entity")) == 3

def test_atom_ids_unique():
    ids = atom_ids()
    assert len(ids) == len(set(ids))

def test_compose_all():
    g = compose()
    assert g["node_count"] == 90
    assert g["scoped_completion"] is False
    assert g["unscoped_completion"] == "undefined"

def test_compose_subset():
    g = compose(atom_ids()[:5])
    assert g["node_count"] == 5
