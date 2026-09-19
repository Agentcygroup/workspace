import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate.typesys import (
    Refusal, RULES, UNIT, NAME, NAT, BOOL,
    arrow, pair_ty, seq_ty, map_ty,
    T_Unit, T_Name, T_Bool, T_Nat, T_Pair, T_Seq, T_Map, T_Fn,
    T_Compose, T_Quote,
)


def test_ten_rules():
    assert len(RULES) == 10


def test_primitive_judgments():
    assert T_Unit("u").type.kind == "unit"
    assert T_Name("n").type.kind == "name"
    assert T_Bool("b").type.kind == "bool"
    assert T_Nat("i").type.kind == "nat"


def test_pair_of_different_types():
    j = T_Pair(T_Name("x"), T_Nat("3"))
    assert j.type.kind == "pair"
    assert j.type.parts[0].kind == "name"
    assert j.type.parts[1].kind == "nat"


def test_seq_requires_homogeneous():
    good = T_Seq((T_Nat("1"), T_Nat("2"), T_Nat("3")))
    assert good.type.kind == "seq"
    try:
        T_Seq((T_Nat("1"), T_Name("x")))
        assert False
    except Refusal as e:
        assert "heterogeneous" in e.code


def test_seq_rejects_empty():
    try:
        T_Seq(())
        assert False
    except Refusal as e:
        assert "empty" in e.code


def test_fn_builds_arrow():
    body = T_Nat("body")
    j = T_Fn("x", NAT, body)
    assert j.type.kind == "→"
    assert j.type.parts[0].kind == "nat"
    assert j.type.parts[1].kind == "nat"


def test_compose_requires_matching_codomain_domain():
    g = T_Fn("x", NAT, T_Nat("g"))
    f = T_Fn("y", NAT, T_Nat("f"))
    j = T_Compose(g, f)
    assert j.type.kind == "→"


def test_compose_rejects_type_mismatch():
    g = T_Fn("x", NAT, T_Nat("g"))       # nat → nat
    f = T_Fn("y", NAME, T_Name("f"))     # name → name
    try:
        T_Compose(g, f)
        assert False
    except Refusal as e:
        assert "mismatch" in e.code


def test_compose_rejects_non_arrows():
    n = T_Nat("3")
    try:
        T_Compose(n, n)
        assert False
    except Refusal as e:
        assert "not-arrows" in e.code


def test_quote_produces_ref():
    j = T_Quote(T_Nat("3"))
    assert j.type.kind == "ref"
    assert j.type.parts[0].kind == "nat"


def test_map_homogeneous():
    entries = ((T_Name("k1"), T_Nat("1")), (T_Name("k2"), T_Nat("2")))
    j = T_Map(entries)
    assert j.type.kind == "map"


def test_map_heterogeneous_refused():
    entries = ((T_Name("k1"), T_Nat("1")), (T_Name("k2"), T_Name("x")))
    try:
        T_Map(entries)
        assert False
    except Refusal as e:
        assert "heterogeneous" in e.code


def test_judgment_records_rule_and_premises():
    j = T_Compose(T_Fn("x", NAT, T_Nat("g")), T_Fn("y", NAT, T_Nat("f")))
    assert j.rule == "T-Compose"
    assert len(j.premises) == 2


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
