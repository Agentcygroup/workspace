import pytest
from complexity import CLASSES, RELATIONS, Class, dominates, is_class

def test_classes_nonempty():
    assert len(CLASSES) >= 10

def test_class_bad_name():
    with pytest.raises(ValueError):
        Class("O(taco)")

def test_dominates_reflexive():
    assert dominates("O(n)","O(n)")

def test_dominates_transitive():
    assert dominates("O(n^2)","O(log n)")
    assert dominates("O(n!)","O(1)")

def test_does_not_dominate():
    assert not dominates("O(1)","O(n)")

def test_is_class():
    assert is_class("polynomial")
    assert not is_class("O(taco)")
