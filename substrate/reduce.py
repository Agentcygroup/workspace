"""Reduction rules: a term reduces to a normal form by named rules.

The semantics in substrate/semantics.py says what a term denotes.
The types in substrate/typesys.py says what a term is.
This file says how a term evaluates — step by step, by named rules.

Rules (each has a name, a pattern, and a result):

  β-compose   compose(f, g) applied to x   →  f(g(x))
  β-fst       fst(product(a, b))           →  a
  β-snd       snd(product(a, b))           →  b
  β-quote     quote(t) applied to ()       →  t
  β-derive    derive(t, r)                 →  t
  β-if-left   if(sum_left(a,b))            →  a
  β-if-right  if(sum_right(a,b))           →  b

A term is in normal form if no rule applies. Reduction is total on
well-typed terms: if a term has a type and is not in normal form,
exactly one rule applies. If two rules would apply, that is a
Refusal — the rules are not confluent.

The reducer does not guess. It matches patterns and refuses on
anything that is not a rule application.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from substrate.typesys import Refusal


# --- the term shape used by the reducer ------------------------------------
# The reducer works on the Term shape from substrate/__init__.py, but the
# Term there is a dataclass with a `body` field. The reducer uses that
# body directly. This keeps one term shape for the whole substrate.

@dataclass(frozen=True)
class ReduceStep:
    rule: str
    before: Any
    after: Any


@dataclass(frozen=True)
class ReduceResult:
    normal: Any
    steps: tuple[ReduceStep, ...]
    terminal_rule: str               # the last rule that applied, or "value"


def _is_compose_application(body: Any) -> bool:
    return (isinstance(body, tuple) and len(body) == 3
            and body[0] == "compose-app")


def _is_product(body: Any) -> bool:
    return (isinstance(body, tuple) and len(body) == 3
            and body[0] in ("product-fst", "product-snd"))


def _is_sum(body: Any) -> bool:
    return (isinstance(body, tuple) and len(body) == 3
            and body[0] in ("sum-left", "sum-right"))


def _is_quote(body: Any) -> bool:
    return (isinstance(body, tuple) and len(body) == 2
            and body[0] == "quote")


def _is_derive(body: Any) -> bool:
    return (isinstance(body, tuple) and len(body) == 3
            and body[0] == "derive")


def step(body: Any) -> ReduceStep | None:
    """One reduction step, or None if body is in normal form."""
    if _is_compose_application(body):
        # body = ("compose-app", (f, g), x)
        _, (f, g), x = body
        if not callable(f) or not callable(g):
            raise Refusal("substrate.reduce.compose.not-fn",
                          "compose-app needs two functions")
        return ReduceStep(rule="β-compose", before=body, after=f(g(x)))

    if _is_product(body):
        # ("product-fst", a, b) or ("product-snd", a, b)
        tag, a, b = body
        if tag == "product-fst":
            return ReduceStep(rule="β-fst", before=body, after=a)
        if tag == "product-snd":
            return ReduceStep(rule="β-snd", before=body, after=b)

    if _is_quote(body) and len(body) == 2:
        _, t = body
        return ReduceStep(rule="β-quote", before=body, after=t)

    if _is_derive(body):
        _, t, _r = body
        return ReduceStep(rule="β-derive", before=body, after=t)

    if _is_sum(body):
        tag, a, b = body
        if tag == "sum-left":
            return ReduceStep(rule="β-if-left", before=body, after=a)
        if tag == "sum-right":
            return ReduceStep(rule="β-if-right", before=body, after=b)

    return None


def reduce(body: Any, max_steps: int = 1000) -> ReduceResult:
    """Reduce to normal form. Refuses if no progress after max_steps."""
    steps: list[ReduceStep] = []
    current = body
    for _ in range(max_steps):
        s = step(current)
        if s is None:
            return ReduceResult(
                normal=current,
                steps=tuple(steps),
                terminal_rule=steps[-1].rule if steps else "value",
            )
        steps.append(s)
        current = s.after
    raise Refusal("substrate.reduce.no-progress",
                  f"no normal form after {max_steps} steps")


def is_value(body: Any) -> bool:
    """A body is a value if no rule applies to it."""
    return step(body) is None


# --- constructors for terms the reducer can act on -------------------------
# These build the tuple shapes the rules match. They do not go through
# substrate/__init__.py's atom/compose because those build Terms with
# ids. The reducer works on bodies.

def compose_app(f: Any, g: Any, x: Any) -> tuple:
    return ("compose-app", (f, g), x)


def product_fst(a: Any, b: Any) -> tuple:
    return ("product-fst", a, b)


def product_snd(a: Any, b: Any) -> tuple:
    return ("product-snd", a, b)


def quote(t: Any) -> tuple:
    return ("quote", t)


def derive(t: Any, rule: str) -> tuple:
    if not isinstance(rule, str) or not rule:
        raise Refusal("substrate.reduce.derive.no-rule",
                      "derive needs a non-empty rule name")
    return ("derive", t, rule)


def sum_left(a: Any, b: Any) -> tuple:
    return ("sum-left", a, b)


def sum_right(a: Any, b: Any) -> tuple:
    return ("sum-right", a, b)


RULES = ("β-compose", "β-fst", "β-snd", "β-quote", "β-derive",
         "β-if-left", "β-if-right")


__all__ = [
    "ReduceStep", "ReduceResult", "Refusal", "RULES",
    "step", "reduce", "is_value",
    "compose_app", "product_fst", "product_snd",
    "quote", "derive", "sum_left", "sum_right",
]
