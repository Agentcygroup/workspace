import math

def dot(a, b):
    if len(a) != len(b):
        raise ValueError("length mismatch")
    return sum(x*y for x, y in zip(a, b))

def axpy(alpha, x, y):
    if len(x) != len(y):
        raise ValueError("length mismatch")
    return [alpha*xi + yi for xi, yi in zip(x, y)]

def relu(x):
    return [max(0.0, v) for v in x]

def sigmoid(x):
    return [1.0 / (1.0 + math.exp(-v)) for v in x]

def softmax(x):
    if not x:
        return []
    m = max(x)
    ex = [math.exp(v - m) for v in x]
    s = sum(ex)
    return [e / s for e in ex]
