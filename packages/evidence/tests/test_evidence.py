from evidence import EvidenceRef, Provenance, hash_bytes, hash_file

def test_hash_bytes_stable():
    assert hash_bytes(b"x") == hash_bytes(b"x")

def test_hash_file(tmp_path):
    p = tmp_path / "f.txt"
    p.write_text("hello")
    h1 = hash_file(p)
    p.write_text("hello")
    assert hash_file(p) == h1

def test_evidence_ref():
    e = EvidenceRef("E-001","path","strong","abc","2026")
    assert e.evidence_id == "E-001"

def test_provenance_chain():
    p = Provenance()
    p.add("alice","read","a.txt")
    p.add("bob","write","b.txt")
    assert len(p.steps) == 2

def test_provenance_validate():
    p = Provenance()
    p.add("alice","read","a.txt")
    assert p.validate() == []
    p.add("", "", "")
    assert p.validate()
