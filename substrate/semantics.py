"""Denotational semantics for the nine primitives.

Each primitive denotes a domain. A Term denotes an element of the
domain of its kind. The semantics is a total function from Term to
a Python value in the denoted domain; it is not a tag lookup.

  unit   ↦  {⊥}                     one element
  name   ↦  Σ*                      finite strings
  bool   ↦  {⊤, ⊥}                  two elements
  nat    ↦  ℕ                       non-negative integers
  pair   ↦  A × B                   cartesian product
  seq    ↦  A*                      finite sequences
  map    ↦  K ⇀ V                   finite partial functions
  fn     ↦  A → B                   total functions
  ref    ↦  Term                    the terms themselves

The last line closes the circle: a Term can denote a Term. That is
the recursion that makes the substrate closed.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


class Refusal(Exception):
    def __init__(self, code: str, reason: str):
        super().__init__(f"{code}: {reason}")
        self.code = code
        self.reason = reason


# --- the domain of each primitive -----------------------------------------

@dataclass(frozen=True)
class Domain:
    name: str
    admits: tuple[type, ...]
    describe: str


DOMAINS: dict[str, Domain] = {
    "unit":  Domain("unit",  (type(None),),  "the one-element domain {⊥}"),
    "name":  Domain("name",  (str,),         "finite strings Σ*"),
    "bool":  Domain("bool",  (bool,),        "the two-element domain {⊤,⊥}"),
    "nat":   Domain("nat",   (int,),         "non-negative integers ℕ"),
    "pair":  Domain("pair",  (tuple,),       "cartesian product A × B"),
    "seq":   Domain("seq",   (tuple,),       "finite sequences A*"),
    "map":   Domain("map",   (dict,),        "finite partial functions K ⇀ V"),
    "fn":    Domain("fn",    (type(lambda: 0),), "total functions A → B"),
    "ref":   Domain("ref",   (str, object),  "the terms themselves"),
}


def denotes(kind: str, value: Any) -> Any:
    """The denotation of a primitive value. Total on its domain.

    Raises Refusal(substrate.semantics.out-of-domain.<kind>) if value
    is not an element of the denoted domain. There is no coercion.
    """
    if kind not in DOMAINS:
        raise Refusal(f"substrate.semantics.unknown-domain.{kind}",
                      f"{kind!r} does not denote a domain")
    d = DOMAINS[kind]
    # nat excludes bool explicitly (bool is a subtype of int in Python).
    if kind == "nat":
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise Refusal(f"substrate.semantics.out-of-domain.{kind}",
                          f"{value!r} ∉ ℕ")
        return value
    if kind == "seq":
        if not isinstance(value, tuple):
            raise Refusal("substrate.semantics.out-of-domain.seq",
                          f"{value!r} ∉ A*")
        return value
    if kind == "pair":
        if not isinstance(value, tuple) or len(value) != 2:
            raise Refusal("substrate.semantics.out-of-domain.pair",
                          f"{value!r} ∉ A × B")
        return value
    if kind == "fn":
        if not callable(value):
            raise Refusal("substrate.semantics.out-of-domain.fn",
                          f"{value!r} ∉ A → B")
        return value
    if kind == "map":
        if not isinstance(value, dict):
            raise Refusal("substrate.semantics.out-of-domain.map",
                          f"{value!r} ∉ K ⇀ V")
        return value
    if not isinstance(value, d.admits):
        raise Refusal(f"substrate.semantics.out-of-domain.{kind}",
                      f"{value!r} ∉ {d.describe}")
    return value


# --- semantics of the six constructors ------------------------------------

def denote_atom(kind: str, value: Any) -> Any:
    return denotes(kind, value)


def denote_compose(f: Any, g: Any, x: Any) -> Any:
    """⟦compose(f,g)⟧(x) = ⟦f⟧(⟦g⟧(x)). The composition law."""
    if not callable(f) or not callable(g):
        raise Refusal("substrate.semantics.compose.not-fn",
                      f"compose needs functions, got {type(f).__name__}, {type(g).__name__}")
    return f(g(x))


def denote_product(a: Any, b: Any) -> tuple:
    return (a, b)


def denote_sum_left(a: Any, b: Any) -> tuple:
    return ("left", a)


def denote_sum_right(a: Any, b: Any) -> tuple:
    return ("right", b)


def denote_quote(t: Any) -> Any:
    """⟦quote(t)⟧ = t. The quotation law: the denotation of quote(t) is t."""
    return t


def denote_derive(t: Any, rule: str) -> Any:
    """⟦derive(t, r)⟧ = ⟦t⟧. Derivation records, does not change denotation."""
    if not isinstance(rule, str) or not rule:
        raise Refusal("substrate.semantics.derive.no-rule",
                      "derive needs a non-empty rule name")
    return t


# --- equations the semantics must satisfy ----------------------------------
# These are the laws. They are checked by the tests. They are the reason
# the substrate has a semantics and not just a shape.

LAWS = (
    ("compose-assoc",
     "⟦compose(compose(f,g),h)⟧ = ⟦compose(f,compose(g,h))⟧"),
    ("compose-id-left",
     "⟦compose(id,f)⟧ = ⟦f⟧"),
    ("compose-id-right",
     "⟦compose(f,id)⟧ = ⟦f⟧"),
    ("quote-involution",
     "⟦quote(quote(t))⟧ = ⟦quote(t)⟧"),
    ("derive-preserves",
     "⟦derive(t,r)⟧ = ⟦t⟧"),
    ("product-fst",
     "fst(⟦product(a,b)⟧) = ⟦a⟧"),
    ("product-snd",
     "snd(⟦product(a,b)⟧) = ⟦b⟧"),
)


__all__ = [
    "Domain", "DOMAINS", "Refusal", "LAWS",
    "denotes",
    "denote_atom", "denote_compose", "denote_product",
    "denote_sum_left", "denote_sum_right",
    "denote_quote", "denote_derive",
]
