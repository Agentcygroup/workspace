def quantize_scalar(value, scale, zero_point, bits=8):
    if bits < 1 or bits > 32:
        raise ValueError("bits must be in [1,32]")
    qmin = 0
    qmax = (1 << bits) - 1
    q = round(value / scale) + zero_point
    q = max(qmin, min(qmax, q))
    return q

def dequantize_scalar(q, scale, zero_point):
    return (q - zero_point) * scale

def quantization_error(value, scale, zero_point, bits=8):
    q = quantize_scalar(value, scale, zero_point, bits)
    return abs(value - dequantize_scalar(q, scale, zero_point))
