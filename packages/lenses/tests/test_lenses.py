from lenses import LENSES, Lens, lens_questions, is_lens

def test_lenses_nonempty():
    assert len(LENSES) >= 25

def test_is_lens():
    assert is_lens("security")
    assert not is_lens("tacos")

def test_lens_questions_security():
    q = lens_questions("security")
    assert any("attacker" in x for x in q)

def test_lens_default_question():
    assert lens_questions("unknown_lens")

def test_lens_ask():
    l = Lens("security", ["q1","q2"])
    assert l.ask() == ["q1","q2"]
