import pytest
from certificate import Certificate, SIGNERS

def test_construct():
    c = Certificate("CERT-1","scope",["CF-1"])
    assert not c.is_signed()

def test_sign():
    c = Certificate("CERT-1","scope",["CF-1"])
    c.sign("human.eve","SIGDATA")
    assert c.is_signed()

def test_no_conformance():
    c = Certificate("CERT-1","scope",[])
    with pytest.raises(ValueError):
        c.sign("a","b")

def test_no_signer():
    c = Certificate("CERT-1","scope",["CF-1"])
    with pytest.raises(ValueError):
        c.sign("","b")

def test_role_closed():
    assert len(SIGNERS) == 1
    assert SIGNERS[0] == "H5_certifying_officer"
