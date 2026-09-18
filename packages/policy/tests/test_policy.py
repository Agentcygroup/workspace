from policy import Rule, Policy, Decision, ALLOW, DENY

def test_default_deny():
    p = Policy()
    d = p.evaluate({})
    assert d.effect == DENY
    assert d.rule_name == "<default>"

def test_allow_rule():
    p = Policy()
    p.add(Rule("allow_x", ALLOW, lambda c: c.get("x") == 1))
    assert p.evaluate({"x":1}).effect == ALLOW

def test_priority():
    p = Policy()
    p.add(Rule("low", ALLOW, lambda c: True, priority=1))
    p.add(Rule("high", DENY, lambda c: True, priority=10))
    assert p.evaluate({}).rule_name == "high"

def test_bad_effect():
    try:
        Policy().add(Rule("x","maybe",lambda c: True))
        assert False
    except ValueError:
        pass

def test_condition_error_denies():
    p = Policy()
    def boom(c): raise RuntimeError("x")
    p.add(Rule("boom", ALLOW, boom))
    d = p.evaluate({})
    assert d.effect == DENY
    assert "error" in d.reason
