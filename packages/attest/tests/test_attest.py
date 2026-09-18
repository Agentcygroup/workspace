import json
from pathlib import Path
from attest import Statement, Subject, build_statement, SBOM, generate_sbom
from attest.statement import sha_file

def test_subject_digest(tmp_path):
    p = tmp_path / "f.txt"
    p.write_text("hello")
    h = sha_file(p)
    assert len(h) == 64

def test_build_statement(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("x")
    s = build_statement("test", {"purpose":"demo"}, [p])
    assert len(s.subjects) == 1
    assert s.subjects[0].name == "a.txt"
    d = s.to_dict()
    assert d["_type"].startswith("https://in-toto.io")

def test_statement_hash_stable(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("x")
    s1 = build_statement("t", {}, [p])
    s2 = build_statement("t", {}, [p])
    s1.created_utc = s2.created_utc = "2026"
    assert s1.hash() == s2.hash()

def test_sbom_cyclonedx_shape():
    sb = SBOM()
    sb.add("foo","1.0")
    d = sb.to_cyclonedx()
    assert d["bomFormat"] == "CycloneDX"
    assert len(d["components"]) == 1

def test_generate_sbom_returns_dict():
    d = generate_sbom()
    assert d["bomFormat"] == "CycloneDX"
    assert isinstance(d["components"], list)
