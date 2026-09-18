from .scalar import quantize_scalar, dequantize_scalar

def _bounds(xs):
    return min(xs), max(xs)

def quantize_tensor(xs, bits=8):
    if not xs:
        raise ValueError("empty tensor")
    lo, hi = _bounds(xs)
    qmax = (1 << bits) - 1
    scale = (hi - lo) / qmax if hi != lo else 1.0
    zero_point = 0
    qs = [quantize_scalar(x, scale, zero_point, bits) for x in xs]
    return {"scale": scale, "zero_point": zero_point, "bits": bits, "values": qs}

def dequantize_tensor(q, bits=8):
    scale = q["scale"]; zp = q["zero_point"]
    return [dequantize_scalar(v, scale, zp) for v in q["values"]]
