import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate.udag import denotes_udag


def test_empty_graph():
    assert denotes_udag((set(), set())).ok is True


def test_single_node():
    assert denotes_udag(({1}, set())).ok is True


def test_chain():
    v = denotes_udag(({1,2,3}, {(1,2),(2,3)}))
    assert v.ok is True and v.nodes == 3 and v.edges == 2


def test_star():
    assert denotes_udag(({1,2,3}, {(1,2),(1,3)})).ok is True


def test_triangle_is_cycle():
    v = denotes_udag(({1,2,3}, {(1,2),(2,3),(3,1)}))
    assert v.ok is False and "cycle" in v.reason


def test_self_loop_refused():
    v = denotes_udag(({1,2}, {(1,1)}))
    assert v.ok is False and "self loop" in v.reason


def test_duplicate_undirected_edge_refused():
    v = denotes_udag(({1,2}, {(1,2),(2,1)}))
    assert v.ok is False and "duplicate" in v.reason


def test_unknown_node_refused():
    v = denotes_udag(({1,2}, {(1,3)}))
    assert v.ok is False and "unknown" in v.reason


def test_malformed_input_refused():
    v = denotes_udag("not a graph")
    assert v.ok is False


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
