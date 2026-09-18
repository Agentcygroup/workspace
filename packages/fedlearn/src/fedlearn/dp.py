import random

def clip(vector, bound):
    if bound <= 0:
        raise ValueError("bound must be positive")
    norm = sum(v*v for v in vector) ** 0.5
    if norm <= bound:
        return list(vector)
    factor = bound / norm
    return [v * factor for v in vector]

def add_noise(vector, sigma, rng=None):
    rng = rng or random.Random()
    return [v + rng.gauss(0, sigma) for v in vector]

def dp_mean(vectors, bound, sigma, rng=None):
    if not vectors:
        raise ValueError("no vectors")
    rng = rng or random.Random()
    clipped = [clip(v, bound) for v in vectors]
    dim = len(clipped[0])
    sums = [sum(c[i] for c in clipped) for i in range(dim)]
    means = [s / len(clipped) for s in sums]
    return add_noise(means, sigma, rng)
