"""Ten semantic operators. Each with a denotation and a pure implementation."""
__version__ = "0.1.0"
from typing import Any, Callable

def _id(x): return x
def _neg(x): return not x
def _count(x):
    try: return len(x)
    except TypeError: return 1
def _merge(xs):
    if not isinstance(xs, list): raise TypeError("merge needs list")
    out = []
    for x in xs:
        if isinstance(x, list): out.extend(x)
        else: out.append(x)
    return out
def _split(x, n=2):
    if not isinstance(x, list): raise TypeError("split needs list")
    if n < 1: raise ValueError("n must be >= 1")
    size = max(1, len(x) // n)
    return [x[i:i+size] for i in range(0, len(x), size)]
def _filter(pred, xs):
    return [x for x in xs if pred(x)]
def _map(fn, xs):
    return [fn(x) for x in xs]
def _fold(init, fn, xs):
    acc = init
    for x in xs: acc = fn(acc, x)
    return acc
def _align(a, b):
    keys = set(a) & set(b)
    return {k: (a[k], b[k]) for k in sorted(keys)}
def _project(keys, d):
    return {k: d[k] for k in keys if k in d}

OPERATORS = {
    "id": {"arity": 1, "denotation": "returns its argument unchanged", "fn": _id},
    "neg": {"arity": 1, "denotation": "boolean negation", "fn": _neg},
    "count": {"arity": 1, "denotation": "cardinality of iterable or 1", "fn": _count},
    "merge": {"arity": 1, "denotation": "flatten one level of a list", "fn": _merge},
    "split": {"arity": 2, "denotation": "partition a list into n roughly equal parts", "fn": _split},
    "filter": {"arity": 2, "denotation": "keep items satisfying a predicate", "fn": _filter},
    "map": {"arity": 2, "denotation": "apply a function to each item", "fn": _map},
    "fold": {"arity": 3, "denotation": "left fold with initial value", "fn": _fold},
    "align": {"arity": 2, "denotation": "intersect two dicts on keys, keep both values", "fn": _align},
    "project": {"arity": 2, "denotation": "restrict a dict to a set of keys", "fn": _project},
}

def apply_operator(name, *args):
    spec = OPERATORS.get(name)
    if spec is None:
        raise ValueError("unknown operator: " + name)
    if len(args) != spec["arity"]:
        raise ValueError(f"{name} expects {spec[chr(34)+chr(97)+chr(114)+chr(105)+chr(116)+chr(121)+chr(34)]} args, got {len(args)}")
    return spec["fn"](*args)

def denotation(name):
    spec = OPERATORS.get(name)
    return spec["denotation"] if spec else None
