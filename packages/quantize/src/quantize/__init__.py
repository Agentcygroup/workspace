"""Quantize: scalar and per-channel quantization of numeric tensors."""
__version__ = "0.1.0"
from .scalar import quantize_scalar, dequantize_scalar, quantization_error
from .tensor import quantize_tensor, dequantize_tensor
