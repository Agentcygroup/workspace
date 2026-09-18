from sovereignty import Jurisdiction, Boundary, Route, RouteDecision

def test_permit_default():
    b = Boundary(Jurisdiction("EU"))
    assert b.permits("US")

def test_permit_blocked():
    b = Boundary(Jurisdiction("EU"), blocked_egress=["XX"])
    assert not b.permits("XX")

def test_permit_allowlist():
    b = Boundary(Jurisdiction("EU"), allowed_egress=["US"])
    assert b.permits("US")
    assert not b.permits("JP")

def test_route_allow():
    s = Boundary(Jurisdiction("EU"))
    t = Boundary(Jurisdiction("US"))
    r = Route(s, t).evaluate()
    assert r.allow

def test_route_blocked():
    s = Boundary(Jurisdiction("EU"), blocked_egress=["US"])
    t = Boundary(Jurisdiction("US"))
    r = Route(s, t).evaluate()
    assert not r.allow

def test_residency_blocks_personal():
    s = Boundary(Jurisdiction("EU"))
    t = Boundary(Jurisdiction("US", residency_required=True))
    r = Route(s, t).evaluate(payload_kind="personal")
    assert not r.allow
