import pytest
from hands_cs import HANDS, Hand, hands_by_family, is_hand

def test_hands_nonempty():
    assert len(HANDS) >= 30

def test_is_hand():
    assert is_hand("code")
    assert not is_hand("nonsense")

def test_hand_upgrade():
    h = Hand("code")
    h.upgrade("expert")
    assert h.proficiency == "expert"

def test_hand_bad_level():
    h = Hand("code")
    with pytest.raises(ValueError):
        h.upgrade("godlike")

def test_families():
    f = hands_by_family()
    assert "build" in f
    assert "protect" in f
