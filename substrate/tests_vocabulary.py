import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate import Term
from substrate.vocabulary import (
    LEVELS, DIMENSIONS, GATEWAY, GATEWAY_VERBS, ENTERPRISE_GRAPH,
    INVARIANTS, check,
)


def test_six_levels():
    assert len(LEVELS.body) == 6


def test_levels_are_axioms():
    for t in LEVELS.body:
        assert t.kind == "derived"
        assert t.type.startswith("axiom:level:")


def test_nine_dimensions():
    assert len(DIMENSIONS.body) == 9


def test_dimensions_are_grammars():
    for t in DIMENSIONS.body:
        assert t.kind == "derived"
        assert t.type.startswith("grammar:")


def test_forty_seven_verbs():
    assert len(GATEWAY.body) == 47
    assert len(GATEWAY_VERBS) == 47


def test_verbs_are_functions():
    for t in GATEWAY.body:
        assert t.kind == "fn"
        assert t.type.startswith("gateway:")


def test_verbs_are_executable():
    for t in GATEWAY.body:
        name = t.type.split(":", 1)[1]
        assert t.body() == name


def test_gateway_order_matches_spec():
    for t, name in zip(GATEWAY.body, GATEWAY_VERBS):
        assert t.type == f"gateway:{name}"


def test_enterprise_graph_is_a_term():
    assert isinstance(ENTERPRISE_GRAPH, Term)
    assert ENTERPRISE_GRAPH.kind == "pair"


def test_all_invariants_hold():
    ok, reason = check()
    assert ok, reason
    assert "levels=6" in reason
    assert "dimensions=9" in reason
    assert "verbs=47" in reason


def test_every_element_is_a_term():
    for t in LEVELS.body + DIMENSIONS.body + GATEWAY.body:
        assert isinstance(t, Term)


def test_terms_have_unique_ids():
    ids = [t.id for t in LEVELS.body + DIMENSIONS.body + GATEWAY.body]
    assert len(ids) == len(set(ids))


def test_enterprise_graph_structure():
    body = ENTERPRISE_GRAPH.body
    assert len(body) == 2
    assert len(body[0]) == 2
    assert body[0][0] == LEVELS.body
    assert body[0][1] == DIMENSIONS.body
    assert body[1] == GATEWAY.body


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
    print(f"\n{ok} ok, {fail} fail")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
