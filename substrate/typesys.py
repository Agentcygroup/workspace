"""Type system: a judgment ⊢ t : T derived from rules.

A type is a Term itself. A judgment is a pair (term_id, type_id) with
a derivation. A judgment is well-formed only if one of the rules below
derives it. There is no other way to get a type.

Rules (all in the substrate's own vocabulary):

  T-Unit    ⊢ atom("unit", None) : unit
  T-Name    ⊢ atom("name", s)   : name
  T-Bool    ⊢ atom("bool", b)   : bool
  T-Nat     ⊢ atom("nat", n)    : nat
  T-Pair    ⊢ a : A   ⊢ b : B
            ────────────────────
            ⊢ product(a,b) : pair(A,B)
  T-Seq     ⊢ t_1 : T ... ⊢ t_n : T
            ─────────────────────────
            ⊢ collection(t_1..t_n) : seq(T)
  T-Map     ⊢ k_i : K   ⊢ v_i : V
            ───────────────────────
            ⊢ state(...) : map(K,V)
  T-Fn      Γ, x:A ⊢ body : B
            ──────────────────
            ⊢ fn(x -> body) : A → B
  T-Compose ⊢ g : A → B   ⊢ f : B → C
            ──────────────────────────
            ⊢ compose(f,g) : A → C
  T-Quote   ⊢ t : T
            ──────────
            ⊢ quote(t) : ref(T)
  T-Ref     ⊢ t : T
            ────────
            ⊢ ref(t) : T

The judgment is a dataclass Judgment(term_id, type_id, rule, premises).
A Judgment is only created by one of the rule functions below. There
is no public constructor.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


class Refusal(Exception):
    def __init__(self, code: str, reason: str):
        super().__init__(f"{code}: {reason}")
        self.code = code
        self.reason = reason


@dataclass(frozen=True)
class Type:
    """A type is a Term in the substrate's vocabulary."""
    id: str
    kind: str                    # primitive name, or "→", or "pair", or "seq", or "map"
    parts: tuple = ()            # sub-types


@dataclass(frozen=True)
class Judgment:
    term_id: str
    type: Type
    rule: str
    premises: tuple = ()


_TY_COUNT = [0]


def _ty(kind: str, *parts: Type) -> Type:
    _TY_COUNT[0] += 1
    return Type(id=f"ty_{_TY_COUNT[0]:05d}", kind=kind, parts=parts)


# --- the primitive type constructors --------------------------------------

UNIT  = _ty("unit")
NAME  = _ty("name")
BOOL  = _ty("bool")
NAT   = _ty("nat")


def arrow(a: Type, b: Type) -> Type:
    return _ty("→", a, b)


def pair_ty(a: Type, b: Type) -> Type:
    return _ty("pair", a, b)


def seq_ty(a: Type) -> Type:
    return _ty("seq", a)


def map_ty(k: Type, v: Type) -> Type:
    return _ty("map", k, v)


def ref_ty(a: Type) -> Type:
    return _ty("ref", a)


# --- the rules ------------------------------------------------------------

def T_Unit(term_id: str) -> Judgment:
    return Judgment(term_id, UNIT, "T-Unit")


def T_Name(term_id: str) -> Judgment:
    return Judgment(term_id, NAME, "T-Name")


def T_Bool(term_id: str) -> Judgment:
    return Judgment(term_id, BOOL, "T-Bool")


def T_Nat(term_id: str) -> Judgment:
    return Judgment(term_id, NAT, "T-Nat")


def T_Pair(a: Judgment, b: Judgment) -> Judgment:
    return Judgment(
        term_id=f"pair({a.term_id},{b.term_id})",
        type=pair_ty(a.type, b.type),
        rule="T-Pair",
        premises=(a, b),
    )


def T_Seq(elements: tuple[Judgment, ...]) -> Judgment:
    if not elements:
        raise Refusal("substrate.typesys.T-Seq.empty",
                      "seq needs at least one element to infer its type")
    first = elements[0].type
    for j in elements[1:]:
        if j.type.id != first.id:
            raise Refusal("substrate.typesys.T-Seq.heterogeneous",
                          f"{j.type.kind} ≠ {first.kind}")
    return Judgment(
        term_id=f"seq({','.join(j.term_id for j in elements)})",
        type=seq_ty(first),
        rule="T-Seq",
        premises=elements,
    )


def T_Map(entries: tuple[tuple[Judgment, Judgment], ...]) -> Judgment:
    if not entries:
        raise Refusal("substrate.typesys.T-Map.empty",
                      "map needs at least one entry to infer its type")
    k0, v0 = entries[0]
    for k, v in entries[1:]:
        if k.type.id != k0.type.id or v.type.id != v0.type.id:
            raise Refusal("substrate.typesys.T-Map.heterogeneous",
                          "all keys must share a type; all values must share a type")
    return Judgment(
        term_id=f"map({len(entries)})",
        type=map_ty(k0.type, v0.type),
        rule="T-Map",
        premises=tuple(j for pair in entries for j in pair),
    )


def T_Fn(param_name: str, param_type: Type, body_judgment: Judgment) -> Judgment:
    return Judgment(
        term_id=f"fn({param_name})",
        type=arrow(param_type, body_judgment.type),
        rule="T-Fn",
        premises=(body_judgment,),
    )


def T_Compose(g: Judgment, f: Judgment) -> Judgment:
    """compose(f, g) : A → C given g : A → B and f : B → C."""
    if g.type.kind != "→" or f.type.kind != "→":
        raise Refusal("substrate.typesys.T-Compose.not-arrows",
                      "both premises must have arrow types")
    if g.type.parts[1].id != f.type.parts[0].id:
        raise Refusal("substrate.typesys.T-Compose.mismatch",
                      f"codomain {g.type.parts[1].kind} ≠ domain {f.type.parts[0].kind}")
    return Judgment(
        term_id=f"compose({f.term_id},{g.term_id})",
        type=arrow(g.type.parts[0], f.type.parts[1]),
        rule="T-Compose",
        premises=(g, f),
    )


def T_Quote(j: Judgment) -> Judgment:
    return Judgment(
        term_id=f"quote({j.term_id})",
        type=ref_ty(j.type),
        rule="T-Quote",
        premises=(j,),
    )


RULES = ("T-Unit", "T-Name", "T-Bool", "T-Nat", "T-Pair",
         "T-Seq", "T-Map", "T-Fn", "T-Compose", "T-Quote")


__all__ = [
    "Type", "Judgment", "Refusal", "RULES",
    "UNIT", "NAME", "BOOL", "NAT",
    "arrow", "pair_ty", "seq_ty", "map_ty", "ref_ty",
    "T_Unit", "T_Name", "T_Bool", "T_Nat", "T_Pair",
    "T_Seq", "T_Map", "T_Fn", "T_Compose", "T_Quote",
]
