from capstone import (
    INSTITUTE_ARCHETYPES, JURISDICTIONS, PLANES, SCOPES,
    make_institute, make_capstone_record, make_interop, validate_capstone,
)
from capstone.schema import build_all


def test_archetypes_nonempty():
    assert len(INSTITUTE_ARCHETYPES) >= 20
    assert "university" in INSTITUTE_ARCHETYPES
    assert "standards_body" in INSTITUTE_ARCHETYPES


def test_jurisdictions():
    assert "EU" in JURISDICTIONS and "US" in JURISDICTIONS


def test_planes():
    assert len(PLANES) == 23


def test_institute_valid():
    i = make_institute("INST-1", "university", "EU", [{"name": "A"}])
    assert i["errors"] == []
    assert i["enrolled"] is False
    assert i["signed_by"] is None


def test_institute_bad_archetype():
    i = make_institute("INST-2", "wizard_tower", "EU", [{"name": "A"}])
    assert any("archetype" in e for e in i["errors"])


def test_institute_bad_jurisdiction():
    i = make_institute("INST-3", "university", "ATLANTIS", [{"name": "A"}])
    assert any("jurisdiction" in e for e in i["errors"])


def test_capstone_record_valid():
    r = make_capstone_record("INST-1", "knowledge", "institutional", "INST-1")
    assert r["errors"] == []


def test_capstone_record_bad_plane():
    r = make_capstone_record("INST-1", "tacos", "institutional", "INST-1")
    assert any("plane" in e for e in r["errors"])


def test_interop_overlap_rejected():
    i = make_interop("INST-1", emits=["knowledge"], consumes=[], refuses=["knowledge"])
    assert any("emitted and refused" in e for e in i["errors"])


def test_validate_duplicate_governor():
    r1 = make_capstone_record("A", "knowledge", "institutional", "A")
    r2 = make_capstone_record("B", "knowledge", "institutional", "B")
    errs = validate_capstone([r1, r2])
    assert any("duplicate governor" in e for e in errs)


def test_build_all(tmp_path):
    written = build_all(tmp_path)
    assert any("institute_archetypes" in w for w in written)
    assert any("example_institute" in w for w in written)
