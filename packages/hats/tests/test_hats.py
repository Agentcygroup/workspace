from hats import HATS, Hat, hats_by_discipline, is_hat

def test_hats_nonempty():
    assert len(HATS) >= 30

def test_is_hat():
    assert is_hat("developer")
    assert not is_hat("wizard")

def test_hat_can():
    h = Hat("developer", capabilities=["write_code"], boundaries=["approve_own_work"])
    assert h.can("write_code")
    assert h.may_not("approve_own_work")

def test_disciplines():
    d = hats_by_discipline()
    assert "engineering" in d
    assert "security" in d
