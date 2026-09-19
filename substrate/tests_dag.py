import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate.dag import denotes_dag, Verdict


def test_empty_graph_is_dag():
    v = denotes_dag((set(), set()))
    assert v.ok is True
    assert v.nodes == 0
    assert v.edges == 0


def test_single_node_is_dag():
    v = denotes_dag(({1}, set()))
    assert v.ok is True


def test_linear_chain_is_dag():
    v = denotes_dag(({1, 2, 3}, {(1, 2), (2, 3)}))
    assert v.ok is True
    assert v.nodes == 3
    assert v.edges == 2


def test_two_node_cycle_is_not_dag():
    v = denotes_dag(({1, 2}, {(1, 2), (2, 1)}))
    assert v.ok is False
    assert "cycle" in v.reason


def test_three_node_cycle_is_not_dag():
    v = denotes_dag(({1, 2, 3}, {(1, 2), (2, 3), (3, 1)}))
    assert v.ok is False


def test_self_loop_is_not_dag():
    v = denotes_dag(({1, 2}, {(1, 1)}))
    assert v.ok is False
    assert "cycle" in v.reason


def test_edge_to_unknown_node_is_not_dag():
    v = denotes_dag(({1, 2}, {(1, 3)}))
    assert v.ok is False
    assert "unknown" in v.reason


def test_malformed_graph_is_not_dag():
    v = denotes_dag("not a graph")
    assert v.ok is False
    assert "pair" in v.reason or "not a" in v.reason


def test_malformed_edge_is_not_dag():
    v = denotes_dag(({1, 2}, {(1, 2, 3)}))
    assert v.ok is False
    assert "ordered pair" in v.reason


def test_diamond_is_dag():
    # 1 -> 2, 1 -> 3, 2 -> 4, 3 -> 4
    v = denotes_dag(({1, 2, 3, 4}, {(1, 2), (1, 3), (2, 4), (3, 4)}))
    assert v.ok is True
    assert v.nodes == 4
    assert v.edges == 4


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
