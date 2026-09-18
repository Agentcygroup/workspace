from metric import SLI, SLO, ErrorBudget

def test_sli_ratio():
    s = SLI("availability", 999, 1000)
    assert abs(s.ratio() - 0.999) < 1e-9

def test_sli_empty():
    assert SLI("x",0,0).ratio() == 1.0

def test_slo_bad_target():
    try:
        SLO("x", 1.5)
        assert False
    except ValueError:
        pass

def test_budget_consumed_zero():
    b = ErrorBudget(SLO("x", 0.999))
    assert b.consumed(SLI("x", 1000, 1000)) == 0.0

def test_budget_consumed_full():
    b = ErrorBudget(SLO("x", 0.999))
    assert b.consumed(SLI("x", 0, 1000)) == 1.0

def test_burn_rate_positive():
    b = ErrorBudget(SLO("x", 0.999))
    r = b.burn_rate(SLI("x", 500, 1000), 1)
    assert r > 1.0
