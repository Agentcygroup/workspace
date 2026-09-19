import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate import Term
from substrate.graphs import (
    GRAPH_NAMES, GRAPH_ACRONYMS, KERNEL, OBSERVABLE, F,
    DISTINCTION, PERSISTENCE, LINKAGE, TRANSFORMATION, EVIDENCE,
    ID_FIELD, STATE_FIELD, REL_FIELD, PROC_FIELD, EVID_FIELD,
    check,
)


def test_graph_count_matches_names():
    assert len(GRAPH_ACRONYMS) == len(GRAPH_NAMES)


def test_graph_names_unique():
    assert len(set(GRAPH_NAMES)) == len(GRAPH_NAMES)


def test_every_graph_is_a_term():
    for t in GRAPH_ACRONYMS:
        assert isinstance(t, Term)
        assert t.kind == "derived"
        assert t.type.startswith("axiom:graph:")


def test_kernel_has_five_parts():
    assert len(KERNEL.body) == 5
    types = {t.type for t in KERNEL.body}
    for required in (
        "axiom:kernel:distinction", "axiom:kernel:persistence",
        "axiom:kernel:linkage", "axiom:kernel:transformation",
        "axiom:kernel:evidence",
    ):
        assert required in types, f"kernel missing {required}"


def test_observable_has_five_fields():
    assert len(OBSERVABLE.body) == 5
    types = {t.type for t in OBSERVABLE.body}
    assert types == {
        "axiom:observable:id", "axiom:observable:state",
        "axiom:observable:rel", "axiom:observable:proc",
        "axiom:observable:evid",
    }


def test_F_is_a_function():
    assert F.kind == "fn"


def test_F_is_composable():
    kinds = [step[0] for step in F.derivation]
    assert "compose" in kinds


def test_check_holds():
    ok, reason = check()
    assert ok, reason
    assert "graphs=" in reason
    assert "kernel=5" in reason
    assert "observable=5" in reason


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
