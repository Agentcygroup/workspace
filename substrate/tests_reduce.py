import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate.reduce import (
    ReduceStep, ReduceResult, Refusal, RULES,
    step, reduce, is_value,
    compose_app, product_fst, product_snd,
    quote, derive, sum_left, sum_right,
)


def test_seven_rules():
    assert len(RULES) == 7


def test_compose_app_reduces():
    inc = lambda x: x + 1
    dbl = lambda x: x * 2
    r = reduce(compose_app(inc, dbl, 3))
    assert r.normal == 7
    assert r.terminal_rule == "β-compose"


def test_fst_reduces():
    r = reduce(product_fst("a", "b"))
    assert r.normal == "a"
    assert r.terminal_rule == "β-fst"


def test_snd_reduces():
    r = reduce(product_snd("a", "b"))
    assert r.normal == "b"
    assert r.terminal_rule == "β-snd"


def test_quote_reduces_to_inner():
    r = reduce(quote(42))
    assert r.normal == 42
    assert r.terminal_rule == "β-quote"


def test_derive_reduces_to_inner():
    r = reduce(derive(42, "by-rule"))
    assert r.normal == 42
    assert r.terminal_rule == "β-derive"


def test_derive_rejects_empty_rule():
    try:
        derive(42, "")
        assert False
    except Refusal as e:
        assert "no-rule" in e.code


def test_sum_left_reduces():
    r = reduce(sum_left(1, 2))
    assert r.normal == 1
    assert r.terminal_rule == "β-if-left"


def test_sum_right_reduces():
    r = reduce(sum_right(1, 2))
    assert r.normal == 2
    assert r.terminal_rule == "β-if-right"


def test_value_has_no_step():
    assert is_value(42)
    assert is_value("hello")
    assert step(42) is None


def test_nested_reduction():
    # quote(derive(product_fst(1, 2), "r")) reduces through all three
    body = quote(derive(product_fst(1, 2), "r"))
    r = reduce(body)
    assert r.normal == 1
    assert len(r.steps) == 3
    assert [s.rule for s in r.steps] == ["β-quote", "β-derive", "β-fst"]


def test_reduce_records_all_steps():
    inc = lambda x: x + 1
    body = compose_app(inc, inc, 0)
    r = reduce(body)
    assert len(r.steps) == 1
    s = r.steps[0]
    assert s.rule == "β-compose"
    assert s.before == body
    assert s.after == 2


def test_no_progress_refused():
    # A body that is not a rule application but is also not a value
    # would need a rule to apply. There isn't one. The reducer returns
    # it as the normal form. That is correct: unknown bodies are inert.
    body = ("unrecognized", 1, 2)
    r = reduce(body)
    assert r.normal == body
    assert r.terminal_rule == "value"


def test_compose_app_needs_functions():
    try:
        reduce(compose_app(1, 2, 3))
        assert False
    except Refusal as e:
        assert "not-fn" in e.code


def test_normal_form_is_stable():
    # Reducing a normal form does nothing.
    r1 = reduce(42)
    r2 = reduce(r1.normal)
    assert r1.normal == r2.normal == 42


def test_reduction_is_deterministic():
    inc = lambda x: x + 1
    body = compose_app(inc, inc, 5)
    a = reduce(body)
    b = reduce(body)
    assert a.normal == b.normal
    assert [s.rule for s in a.steps] == [s.rule for s in b.steps]


def main() -> int:
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    ok = fail = 0
    for t in tests:
        try:
            t()
            print(f"  {t.__name__:55} ok")
            ok += 1
        except AssertionError as e:
            print(f"  {t.__name__:55} FAIL {e}")
            fail += 1
        except Refusal as e:
            print(f"  {t.__name__:55} FAIL refusal {e.code}")
            fail += 1
    print(f"\n{ok} ok, {fail} fail")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
