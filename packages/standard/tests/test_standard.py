from standard import STANDARD_VERSION, ARTICLES, MOATS, IMPLEMENTED_MOATS, GAP_MOATS, REFUSALS, refuses, conformance_report
from standard.articles import get_article

def test_version():
    assert STANDARD_VERSION == "1.0.0"

def test_ten_articles():
    assert len(ARTICLES) == 10

def test_ten_moats():
    assert len(MOATS) == 10
    assert len(IMPLEMENTED_MOATS) == 1
    assert len(GAP_MOATS) == 9

def test_gap_names():
    assert "braided_multimodal_fusion" in GAP_MOATS
    assert "orchestration_language" in GAP_MOATS
    assert "reproducible_build_sbom_attestation" not in GAP_MOATS

def test_refusals():
    assert refuses("compliance_without_signature")
    assert refuses("agi_without_test")
    assert refuses("transport_without_invocation")
    assert refuses("completion_of_open_domain")
    assert refuses("promise_document")
    assert refuses("package_name_overreach")
    assert not refuses("some_other_claim")

def test_articles_named():
    for i in range(1, 11):
        assert get_article(i) is not None

def test_conformance_report():
    r = conformance_report()
    assert r["standard_version"] == "1.0.0"
    assert r["articles"] == 10
    assert r["refusals"] == 6
    assert r["moats_total"] == 10
    assert r["moats_implemented"] == 1
    assert r["moats_gap"] == 9
    assert r["scoped_completion"] is False
    assert r["unscoped_completion"] == "undefined"
