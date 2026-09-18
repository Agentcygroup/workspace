import pytest
from queuekit import FIFO, QueueFull, QueueEmpty

def test_push_pop():
    q = FIFO(2)
    q.push(1); q.push(2)
    assert q.pop() == 1
    assert q.pop() == 2

def test_full():
    q = FIFO(1)
    q.push("x")
    with pytest.raises(QueueFull):
        q.push("y")

def test_empty():
    q = FIFO(1)
    with pytest.raises(QueueEmpty):
        q.pop()

def test_capacity_must_be_positive():
    with pytest.raises(ValueError):
        FIFO(0)
    with pytest.raises(ValueError):
        FIFO(-1)

def test_is_full_and_empty():
    q = FIFO(1)
    assert q.is_empty()
    q.push("x")
    assert q.is_full()
    assert not q.is_empty()
