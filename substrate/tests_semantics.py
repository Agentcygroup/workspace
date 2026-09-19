import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate.semantics import (
    DOMAINS, Refusal, LAWS,
    denotes,
    denote_atom, denote_compose, denote_product,
    denote_sum_left, denote_sum_right, denote_quote, denote_derive,
)


def test_nine_domains():
    assert len(DOMAINS) == 9


def test_nat_denotes_integers():
    assert denotes("nat", 3) == 3


def test_nat_rejects_bool():
    try:
        denotes("nat", True)
        assert False
    except Refusal as e:
        assert e.code == "substrate.semantics.out-of-domain.nat"


def test_nat_rejects_negative():
    try:
        denotes("nat", -1)
        assert False
    except Refusal as e:
        assert "out-of-domain" in e.code


def test_name_denotes_string():
    assert denotes("name", "x") == "x"


def test_seq_denotes_tuple():
    assert denotes("seq", (1, 2, 3)) == (1, 2, 3)


def test_fn_denotes_callable():
    f = lambda x: x + 1
    assert denotes("fn", f) is f


def test_atom_denotes_value():
    assert denote_atom("nat", 5) == 5


def test_compose_law():
    inc = lambda x: x + 1
    dbl = lambda x: x * 2
    assert denote_compose(inc, dbl, 3) == 7   # (3*2)+1


def test_compose_assoc():
    f = lambda x: x + 1
    g = lambda x: x * 2
    h = lambda x: x - 3
    for x in range(5):
        # Left association: compose(compose(f, g), h) applied to x
        #   = (compose(f, g)) (h(x))
        #   = f(g(h(x)))
        left = denote_compose(
            lambda y: denote_compose(f, g, y),
            h,
            x,
        )
        # Right association: compose(f, compose(g, h)) applied to x
        #   = f((compose(g, h))(x))
        #   = f(g(h(x)))
        right = denote_compose(
            f,
            lambda y: denote_compose(g, h, y),
            x,
        )
        assert left == right


def test_quote_involution():
    t = ("a", 1)
    assert denote_quote(denote_quote(t)) == denote_quote(t)


def test_derive_preserves_denotation():
    t = 42
    assert denote_derive(t, "by-rule") == 42


def test_derive_needs_rule():
    try:
        denote_derive(42, "")
        assert False
    except Refusal as e:
        assert e.code == "substrate.semantics.derive.no-rule"


def test_product_denotes_pair():
    assert denote_product(1, 2) == (1, 2)


def test_sum_left_right_distinguished():
    assert denote_sum_left(1, 2) == ("left", 1)
    assert denote_sum_right(1, 2) == ("right", 2)
    assert denote_sum_left(1, 2) != denote_sum_right(1, 2)


def test_no_coercion():
    # A string is not a nat. A nat is not a string.
    for kind, bad in [("nat", "3"), ("name", 3), ("bool", 1),
                      ("seq", [1, 2]), ("pair", (1, 2, 3)), ("fn", 42)]:
        try:
            denotes(kind, bad)
            assert False, f"{kind} accepted {bad!r}"
        except Refusal:
            pass


def test_seven_laws_declared():
    assert len(LAWS) == 7


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
