from pattern import PATTERNS, Pattern, by_category, is_pattern

def test_patterns_nonempty():
    assert len(PATTERNS) >= 20

def test_is_pattern():
    assert is_pattern("adapter")
    assert not is_pattern("hologram")

def test_by_category():
    assert len(by_category("creational")) == 4
    assert len(by_category("behavioral")) >= 10
