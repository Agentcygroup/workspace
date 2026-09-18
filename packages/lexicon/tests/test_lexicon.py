from lexicon import TERMS, get_term, terms_by_source, terms_by_atom
from lexicon.validate import validate_term, validate_all
from lexicon.terms import sources

def test_terms_nonempty():
    assert len(TERMS) >= 40

def test_validate_all_clean():
    assert validate_all() == []

def test_get_term():
    t = get_term(TERMS[0]["id"])
    assert t is not None

def test_terms_by_source():
    assert len(terms_by_source("W3C-OWL")) >= 2
    assert len(terms_by_source("emergent")) >= 3

def test_terms_by_atom():
    assert len(terms_by_atom("CON-ENT-001")) >= 2

def test_sources():
    s = sources()
    assert "W3C-OWL" in s
    assert "NIST-800-53" in s
    assert "emergent" in s

def test_every_term_has_primitive():
    for t in TERMS:
        assert t["primitive_id"]

def test_citable_and_emergent_coexist():
    statuses = {t["status"] for t in TERMS}
    assert "citable" in statuses
    assert "emergent" in statuses
