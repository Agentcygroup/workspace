import pytest
from policyplat import Platform, detect_drift
from policy import Policy, Rule, ALLOW, DENY

def test_register_tenant():
    p = Platform()
    p.register("t1")
    assert "t1" in p.tenants

def test_duplicate_tenant():
    p = Platform()
    p.register("t1")
    with pytest.raises(ValueError):
        p.register("t1")

def test_evaluate_unknown_tenant():
    p = Platform()
    with pytest.raises(KeyError):
        p.evaluate("nope", {})

def test_evaluate_records_audit():
    p = Platform()
    pol = Policy()
    pol.add(Rule("allow_x", ALLOW, lambda c: c.get("x")==1))
    p.register("t1", pol)
    d = p.evaluate("t1", {"x":1})
    assert d.effect == ALLOW
    assert len(p.audit) == 1

def test_audit_report():
    p = Platform()
    pol = Policy()
    pol.add(Rule("allow_x", ALLOW, lambda c: c.get("x")==1))
    p.register("t1", pol)
    p.evaluate("t1", {"x":1})
    p.evaluate("t1", {"x":2})
    r = p.audit_report()
    assert r["total"] == 2
    assert r["by_decision"][ALLOW] == 1
    assert r["by_decision"][DENY] == 1

def test_drift_detected():
    p1 = Policy()
    p1.add(Rule("a", ALLOW, lambda c: c.get("x")==1))
    p2 = Policy()
    p2.add(Rule("a", DENY, lambda c: c.get("x")==1))
    changed = detect_drift(p1, p2, [{"x":1},{"x":2}])
    assert len(changed) == 1
    assert changed[0]["was"] == ALLOW
    assert changed[0]["now"] == DENY
