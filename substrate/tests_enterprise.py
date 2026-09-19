import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate import Term
from substrate.enterprise import (
    LAYERS, LAYER_TERMS, ENTERPRISE_VOCABULARY, check,
)


def test_thirty_layers():
    assert len(LAYERS) == 30
    assert len(LAYER_TERMS) == 30


def test_every_layer_is_a_term():
    for name, term in LAYER_TERMS.items():
        assert isinstance(term, Term)
        assert term.type.startswith(f"structure:layer:{name}")


def test_every_item_is_a_term():
    for term in LAYER_TERMS.values():
        for item in term.body:
            assert isinstance(item, Term)
            assert item.kind == "derived"


def test_layer_counts_match_declaration():
    for name, items in LAYERS.items():
        assert len(LAYER_TERMS[name].body) == len(items)


def test_enterprise_vocabulary_is_a_collection():
    assert ENTERPRISE_VOCABULARY.kind == "seq"
    assert len(ENTERPRISE_VOCABULARY.body) == 30


def test_check_holds():
    ok, reason = check()
    assert ok, reason
    assert "layers=30" in reason


def test_layer_names_are_unique():
    names = list(LAYERS.keys())
    assert len(names) == len(set(names))


def test_item_count_total():
    total = sum(len(v) for v in LAYERS.values())
    assert total == 193


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
