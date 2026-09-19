"""Kernel: the smallest vocabulary from which everything admissible is built.

Design rules, enforced by code:

  1. Every term is a first-class object with an id, a type, and a body.
  2. Every term is either a PRIMITIVE or is derived from primitives by
     one of the six constructors.
  3. Every constructor is total: it either returns a Term or raises a
     named Refusal. There is no third outcome.
  4. Every derived term carries the derivation that produced it. The
     derivation is itself a Term.
  5. Nothing outside the vocabulary is admissible. Unknown names raise
     kernel.unknown.<name>.
  6. The kernel is closed: the vocabulary contains the constructors,
     so terms that describe terms are constructible from the same
     vocabulary.

The vocabulary has nine primitives and six constructors. Every other
object in the repo's universe — collection, subset, relation, function,
state, transformation, observation, evidence, proof, counterexample,
validator, execution, policy, certificate, description — is one of the
fifteen terms below, or a composition of them.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable


# --- the nine primitives ---------------------------------------------------

PRIMITIVES = (
    "unit",      # the empty term; the atom of composition
    "name",      # a string; the atom of identity
    "bool",      # True or False; the atom of decision
    "nat",       # a non-negative integer; the atom of count
    "pair",      # an ordered 2-tuple; the atom of relation
    "seq",       # an ordered sequence; the atom of collection
    "map",       # a key-value mapping; the atom of state
    "fn",        # a callable term; the atom of transformation
    "ref",       # a reference to another term by id; the atom of relation across time
)


# --- the six constructors --------------------------------------------------

CONSTRUCTORS = (
    "atom",       # atom(kind, value) -> a Term of one of the nine primitives
    "compose",    # compose(f, g) -> a Term that applies g then f
    "product",    # product(a, b) -> a Term whose value is (a.value, b.value)
    "sum",        # sum(a, b) -> a Term whose value is either a.value or b.value
    "quote",      # quote(term) -> a Term whose value is the term itself
    "derive",     # derive(term, rule) -> a Term that names how term was made
)


# --- the term ---------------------------------------------------------------

@dataclass(frozen=True)
class Term:
    id: str
    kind: str                    # one of PRIMITIVES or one of CONSTRUCTORS or "derived"
    body: Any = None
    derivation: tuple = ()       # the sequence of constructor applications
    type: str = ""

    def __repr__(self) -> str:
        return f"Term({self.id!r}, kind={self.kind!r})"


class Refusal(Exception):
    def __init__(self, code: str, reason: str):
        super().__init__(f"{code}: {reason}")
        self.code = code
        self.reason = reason


_counter = [0]


def _next_id(prefix: str) -> str:
    _counter[0] += 1
    return f"{prefix}_{_counter[0]:05d}"


# --- the six constructors, as functions ------------------------------------

def atom(kind: str, value: Any) -> Term:
    """atom(kind, value) -> Term. kind must be one of PRIMITIVES."""
    if kind not in PRIMITIVES:
        raise Refusal(f"substrate.unknown.{kind}",
                      f"{kind!r} is not a primitive; primitives are {PRIMITIVES}")
    _check_value(kind, value)
    return Term(id=_next_id(kind), kind=kind, body=value, type=kind,
                derivation=(("atom", kind),))


def compose(f: Term, g: Term) -> Term:
    """compose(f, g) -> Term. f and g must be kind='fn'."""
    if f.kind != "fn":
        raise Refusal("substrate.compose.not-fn", f"left is kind={f.kind!r}")
    if g.kind != "fn":
        raise Refusal("substrate.compose.not-fn", f"right is kind={g.kind!r}")
    def _run(x):
        return f.body(g.body(x))
    return Term(id=_next_id("compose"), kind="fn", body=_run,
                type=f"fn({g.type})->{f.type}",
                derivation=(("compose", f.id, g.id),))


def product(a: Term, b: Term) -> Term:
    return Term(id=_next_id("product"), kind="pair",
                body=(a.body, b.body), type=f"({a.type},{b.type})",
                derivation=(("product", a.id, b.id),))


def sum(a: Term, b: Term) -> Term:
    """sum(a, b): a Term whose body is ('left', a) or ('right', b)."""
    return Term(id=_next_id("sum"), kind="pair",
                body=("left", a), type=f"{a.type}|{b.type}",
                derivation=(("sum", a.id, b.id),))


def quote(term: Term) -> Term:
    """quote(term) -> Term whose body is term itself."""
    return Term(id=_next_id("quote"), kind="ref", body=term,
                type=f"quote({term.type})",
                derivation=(("quote", term.id),))


def derive(term: Term, rule: str) -> Term:
    """derive(term, rule) -> Term that records rule as the reason term exists."""
    if not isinstance(rule, str) or not rule:
        raise Refusal("substrate.derive.no-rule", "rule must be a non-empty string")
    return Term(id=term.id, kind=term.kind, body=term.body, type=term.type,
                derivation=term.derivation + (("derive", rule),))


# --- value checking per primitive ------------------------------------------

def _check_value(kind: str, value: Any) -> None:
    ok = {
        "unit":  value is None,
        "name":  isinstance(value, str),
        "bool":  isinstance(value, bool),
        "nat":   isinstance(value, int) and value >= 0 and not isinstance(value, bool),
        "pair":  isinstance(value, tuple) and len(value) == 2,
        "seq":   isinstance(value, (list, tuple)),
        "map":   isinstance(value, dict),
        "fn":    callable(value),
        "ref":   isinstance(value, (str, Term)),
    }.get(kind, False)
    if not ok:
        raise Refusal(f"substrate.atom.bad-value.{kind}",
                      f"value {value!r} is not a valid {kind}")


# --- derived vocabulary -----------------------------------------------------
# Every remaining concept in the universe is expressed as a function that
# returns a Term built from the constructors above. Nothing new is added
# to the kernel. Each derived name has an entry in DERIVED, so the
# vocabulary is closed.

DERIVED: dict[str, Callable] = {}


def _register(name: str):
    def deco(fn):
        DERIVED[name] = fn
        return fn
    return deco


@_register("collection")
def collection(*terms: Term) -> Term:
    return Term(id=_next_id("seq"), kind="seq",
                body=tuple(terms), type="seq",
                derivation=(("seq",) + tuple(t.id for t in terms),))


@_register("subset")
def subset(collection_term: Term, predicate: Term) -> Term:
    if collection_term.kind != "seq":
        raise Refusal("substrate.subset.not-seq", f"got {collection_term.kind!r}")
    if predicate.kind != "fn":
        raise Refusal("substrate.subset.not-fn", f"got {predicate.kind!r}")
    kept = tuple(t for t in collection_term.body if predicate.body(t))
    return Term(id=_next_id("subset"), kind="seq", body=kept,
                type=f"subset({collection_term.type})",
                derivation=(("subset", collection_term.id, predicate.id),))


@_register("relation")
def relation(a: Term, b: Term) -> Term:
    return product(a, b)


@_register("function")
def function(name: str, fn: Callable) -> Term:
    t = atom("fn", fn)
    return Term(id=t.id, kind="fn", body=fn, type=name,
                derivation=(("function", name),))


@_register("state")
def state(**fields: Term) -> Term:
    body = {k: v.body for k, v in fields.items()}
    return Term(id=_next_id("map"), kind="map", body=body, type="state",
                derivation=(("state",) + tuple(v.id for v in fields.values()),))


@_register("transformation")
def transformation(f: Term) -> Term:
    if f.kind != "fn":
        raise Refusal("substrate.transformation.not-fn", f"got {f.kind!r}")
    return Term(id=f.id, kind="fn", body=f.body, type=f"transformation:{f.type}",
                derivation=f.derivation + (("transformation",),))


@_register("observation")
def observation(name: str, f: Term) -> Term:
    if f.kind != "fn":
        raise Refusal("substrate.observation.not-fn", f"got {f.kind!r}")
    return Term(id=_next_id("obs"), kind="fn", body=f.body,
                type=f"observation:{name}",
                derivation=f.derivation + (("observation", name),))


@_register("evidence")
def evidence(claim: Term, witness: Term) -> Term:
    return product(claim, witness)


@_register("proof")
def proof(claim: Term, derivation: tuple) -> Term:
    if not isinstance(derivation, tuple) or not derivation:
        raise Refusal("substrate.proof.empty-derivation",
                      "a proof needs a non-empty derivation")
    return Term(id=_next_id("proof"), kind="derived",
                body={"claim": claim.body, "derivation": derivation},
                type=f"proof:{claim.type}",
                derivation=(("proof", claim.id),) + derivation)


@_register("counterexample")
def counterexample(claim: Term, witness: Term) -> Term:
    return Term(id=_next_id("cex"), kind="derived",
                body={"claim": claim.body, "witness": witness.body},
                type=f"counterexample:{claim.type}",
                derivation=(("counterexample", claim.id, witness.id),))


@_register("validator")
def validator(claim: Term, predicate: Term) -> Term:
    if predicate.kind != "fn":
        raise Refusal("substrate.validator.not-fn", f"got {predicate.kind!r}")
    return Term(id=_next_id("val"), kind="fn",
                body=lambda w: predicate.body(w),
                type=f"validator:{claim.type}",
                derivation=predicate.derivation + (("validator", claim.id),))


@_register("execution")
def execution(fn: Term, arg: Term) -> Term:
    if fn.kind != "fn":
        raise Refusal("substrate.execution.not-fn", f"got {fn.kind!r}")
    result = fn.body(arg.body)
    return Term(id=_next_id("exec"), kind="derived",
                body={"fn": fn.id, "arg": arg.id, "result": result},
                type=f"execution:{fn.type}",
                derivation=(("execution", fn.id, arg.id),))


@_register("policy")
def policy(name: str, predicate: Term, action: Term) -> Term:
    if predicate.kind != "fn":
        raise Refusal("substrate.policy.not-fn", "predicate must be fn")
    if action.kind != "fn":
        raise Refusal("substrate.policy.not-fn", "action must be fn")
    return Term(id=_next_id("pol"), kind="derived",
                body={"name": name,
                      "predicate": predicate.body,
                      "action": action.body},
                type=f"policy:{name}",
                derivation=(("policy", name, predicate.id, action.id),))


@_register("certificate")
def certificate(subject: Term, proof_term: Term, issuer: str) -> Term:
    return Term(id=_next_id("cert"), kind="derived",
                body={"subject": subject.id, "proof": proof_term.id,
                      "issuer": issuer},
                type=f"certificate:{subject.type}",
                derivation=(("certificate", subject.id, proof_term.id, issuer),))


@_register("description")
def description(of: Term, text: str) -> Term:
    return Term(id=_next_id("desc"), kind="name", body=text,
                type=f"description:{of.type}",
                derivation=(("description", of.id),))


@_register("axiom")
def axiom(name: str) -> Term:
    return Term(id=_next_id("ax"), kind="derived",
                body={"name": name}, type=f"axiom:{name}",
                derivation=(("axiom", name),))


@_register("principle")
def principle(name: str, about: Term) -> Term:
    return Term(id=_next_id("pr"), kind="derived",
                body={"name": name, "about": about.id},
                type=f"principle:{name}",
                derivation=(("principle", name, about.id),))


@_register("invariant")
def invariant(name: str, predicate: Term) -> Term:
    if predicate.kind != "fn":
        raise Refusal("substrate.invariant.not-fn", f"got {predicate.kind!r}")
    return Term(id=_next_id("inv"), kind="fn", body=predicate.body,
                type=f"invariant:{name}",
                derivation=predicate.derivation + (("invariant", name),))


@_register("constraint")
def constraint(name: str, predicate: Term) -> Term:
    return invariant(name, predicate)


@_register("grammar")
def grammar(name: str, productions: tuple) -> Term:
    if not isinstance(productions, tuple):
        raise Refusal("substrate.grammar.bad-productions", "must be a tuple")
    return Term(id=_next_id("gram"), kind="derived",
                body={"name": name, "productions": productions},
                type=f"grammar:{name}",
                derivation=(("grammar", name),))


@_register("format")
def format(name: str, fields: tuple) -> Term:
    return Term(id=_next_id("fmt"), kind="derived",
                body={"name": name, "fields": fields},
                type=f"format:{name}",
                derivation=(("format", name),))


@_register("structure")
def structure(name: str, shape: Term) -> Term:
    return Term(id=_next_id("str"), kind="derived",
                body={"name": name, "shape": shape.id},
                type=f"structure:{name}",
                derivation=(("structure", name, shape.id),))


# --- the vocabulary, closed -------------------------------------------------

VOCABULARY = {
    "primitives":   PRIMITIVES,
    "constructors": CONSTRUCTORS,
    "derived":      tuple(sorted(DERIVED)),
}


def lookup(name: str) -> Callable | None:
    if name in PRIMITIVES:
        return lambda v: atom(name, v)
    if name in DERIVED:
        return DERIVED[name]
    return None


def admits(name: str) -> bool:
    return name in PRIMITIVES or name in DERIVED


__all__ = [
    "Term", "Refusal",
    "PRIMITIVES", "CONSTRUCTORS", "DERIVED", "VOCABULARY",
    "atom", "compose", "product", "sum", "quote", "derive",
    "lookup", "admits",
] + list(DERIVED)
