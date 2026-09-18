import pytest
from quantize import quantize_scalar, dequantize_scalar, quantization_error, quantize_tensor, dequantize_tensor

def test_scalar_roundtrip():
    q = quantize_scalar(2.5, 0.1, 0, 8)
    back = dequantize_scalar(q, 0.1, 0)
    assert abs(back - 2.5) < 0.1

def test_scalar_bounds():
    q = quantize_scalar(1e9, 1.0, 0, 8)
    assert q <= 255

def test_bits_validation():
    with pytest.raises(ValueError):
        quantize_scalar(1, 1, 0, 0)

def test_quantization_error():
    e = quantization_error(2.5, 0.1, 0, 8)
    assert e < 0.1

def test_tensor_roundtrip():
    xs = [0.0, 1.0, 2.0, 3.0]
    q = quantize_tensor(xs, 8)
    back = dequantize_tensor(q, 8)
    for a, b in zip(xs, back):
        assert abs(a - b) < 0.05

def test_tensor_empty():
    with pytest.raises(ValueError):
        quantize_tensor([], 8)
