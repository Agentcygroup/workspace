import pytest
from kernels import dot, axpy, relu, sigmoid, softmax, matmul

def test_dot():
    assert dot([1,2,3],[4,5,6]) == 32

def test_dot_mismatch():
    with pytest.raises(ValueError):
        dot([1,2],[1])

def test_axpy():
    assert axpy(2.0, [1,2], [3,4]) == [5.0, 8.0]

def test_relu():
    assert relu([-1, 0, 2]) == [0.0, 0.0, 2.0]

def test_sigmoid():
    s = sigmoid([0.0])
    assert abs(s[0] - 0.5) < 1e-9

def test_softmax_sums_to_one():
    s = softmax([1.0, 2.0, 3.0])
    assert abs(sum(s) - 1.0) < 1e-9

def test_matmul():
    A = [[1,2],[3,4]]
    B = [[5,6],[7,8]]
    assert matmul(A, B) == [[19.0, 22.0], [43.0, 50.0]]

def test_matmul_shape_mismatch():
    with pytest.raises(ValueError):
        matmul([[1,2]], [[1,2]])
