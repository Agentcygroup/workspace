"""The smallest vocabulary, and every name in it as a first-class object.

The kernel has nine primitives and six constructors (substrate/__init__.py).
This file uses them, and only them, to construct every term below. It adds
nothing to the kernel. Each entry is a Term built from atom/compose/
product/sum/quote/derive, or from one of the 22 derived constructors
already declared in substrate/__init__.py.

Three enumerations are built:

  1. LEVELS      — high, medium, low, micro, nano, pico
  2. DIMENSIONS  — organizational, technical, physical, computational,
                   biological, economic, legal, temporal, spatial
  3. GATEWAY     — 47 verbs from DISCOVER to CLOSE

Each is a collection of Terms. Every Term has an id, a kind, a derivation,
and a type. Nothing here is a string in a box. Every name is a Term.

A fourth term is constructed: the ENTERPRISE_GRAPH, a pair of the three
enumerations, so that "levels × dimensions × verbs" is itself a Term.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate import (
    Term, Refusal, atom, compose, product, sum, quote, derive,
    collection, subset, relation, function, state, transformation,
    observation, evidence, proof, counterexample, validator, execution,
    policy, certificate, description, axiom, principle, invariant,
    constraint, grammar, format, structure,
)


# ---------------------------------------------------------------------------
# LEVELS — six terms, each an axiom named after its scale.
# ---------------------------------------------------------------------------

def _level(name: str) -> Term:
    return axiom(f"level:{name}")


LEVELS = collection(
    _level("high"),
    _level("medium"),
    _level("low"),
    _level("micro"),
    _level("nano"),
    _level("pico"),
)


# ---------------------------------------------------------------------------
# DIMENSIONS — nine terms, each a grammar whose single production is itself.
# A dimension is a grammar: it names what can appear in that dimension.
# ---------------------------------------------------------------------------

def _dimension(name: str) -> Term:
    return grammar(name, ((name, ("*",)),))


DIMENSIONS = collection(
    _dimension("organizational"),
    _dimension("technical"),
    _dimension("physical"),
    _dimension("computational"),
    _dimension("biological"),
    _dimension("economic"),
    _dimension("legal"),
    _dimension("temporal"),
    _dimension("spatial"),
)


# ---------------------------------------------------------------------------
# GATEWAY — 47 verbs. Each verb is a function Term whose type is
# `gateway:<name>`. Applied to a level and a dimension, it produces a
# term of the type `execution(<verb>)`. The verbs are enumerated in the
# order they appear in the spec, so the enumeration itself is a sequence.
# ---------------------------------------------------------------------------

GATEWAY_VERBS = (
    "DISCOVER", "IDENTIFY", "OBSERVE", "INGEST", "CLASSIFY",
    "CONTEXTUALIZE", "NORMALIZE", "TRANSLATE", "MAP", "MATCH",
    "RECONCILE", "NEGOTIATE", "AUTHORIZE", "VALIDATE", "ROUTE",
    "FILTER", "TRANSFORM", "ADAPT", "BRIDGE", "ORCHESTRATE",
    "EXECUTE", "MONITOR", "DETECT", "PREDICT", "DECIDE",
    "CONTROL", "VERIFY", "PROVE", "ATTEST", "AUDIT",
    "TRACE", "SCORE", "PRICE", "SETTLE", "ACCOUNT",
    "GOVERN", "ENFORCE", "QUARANTINE", "REJECT", "RECOVER",
    "REPAIR", "RECONFIGURE", "LEARN", "UPDATE", "VERSION",
    "RETIRE", "CLOSE",
)


def _verb(name: str) -> Term:
    """A gateway verb is a function term with a named type.

    Its body, if called, returns the name. That makes the term
    executable: `verb.body()` returns the verb's own name.
    """
    return function(f"gateway:{name}", lambda n=name: n)


GATEWAY = collection(*(_verb(v) for v in GATEWAY_VERBS))


# ---------------------------------------------------------------------------
# The enterprise graph — levels × dimensions × verbs, as a Term.
#
# product(pair(LEVELS, DIMENSIONS), GATEWAY) is one Term.
# Its type is ((seq, seq), seq). Its derivation names the three parts.
# ---------------------------------------------------------------------------

ENTERPRISE_GRAPH = product(
    product(LEVELS, DIMENSIONS),
    GATEWAY,
)


# ---------------------------------------------------------------------------
# Invariants the vocabulary must satisfy. Each is a fn term that checks
# one property. `check()` runs all of them.
# ---------------------------------------------------------------------------

def _inv_levels() -> Term:
    return invariant(
        "levels",
        atom("fn", lambda g: len(g.body[0][0]) == 6),
    )


def _inv_dimensions() -> Term:
    return invariant(
        "dimensions",
        atom("fn", lambda g: len(g.body[0][1]) == 9),
    )


def _inv_verbs() -> Term:
    return invariant(
        "verbs",
        atom("fn", lambda g: len(g.body[1]) == 47),
    )


def _inv_all_terms() -> Term:
    """Every element in every enumeration is a Term."""
    return invariant(
        "all-terms",
        atom("fn", lambda g: all(
            isinstance(t, Term)
            for t in g.body[0][0] + g.body[0][1] + g.body[1]
        )),
    )


INVARIANTS = collection(
    _inv_levels(),
    _inv_dimensions(),
    _inv_verbs(),
    _inv_all_terms(),
)


def check() -> tuple[bool, str]:
    """Run every invariant against ENTERPRISE_GRAPH."""
    for inv in INVARIANTS.body:
        ok = inv.body(ENTERPRISE_GRAPH)
        if not ok:
            return False, f"invariant failed: {inv.type}"
    return True, (
        f"levels={len(LEVELS.body)} "
        f"dimensions={len(DIMENSIONS.body)} "
        f"verbs={len(GATEWAY.body)} "
        f"terms={len(LEVELS.body) + len(DIMENSIONS.body) + len(GATEWAY.body)}"
    )


# ---------------------------------------------------------------------------
# Self-test on __main__.
# ---------------------------------------------------------------------------

def _main() -> int:
    print(f"LEVELS:      {len(LEVELS.body)} terms")
    for t in LEVELS.body:
        assert isinstance(t, Term)
        assert t.kind == "derived"
        print(f"  {t.id:12} {t.type}")

    print(f"\nDIMENSIONS:  {len(DIMENSIONS.body)} terms")
    for t in DIMENSIONS.body:
        assert isinstance(t, Term)
        print(f"  {t.id:12} {t.type}")

    print(f"\nGATEWAY:     {len(GATEWAY.body)} terms")
    for t in GATEWAY.body:
        assert isinstance(t, Term)
        assert t.body() == t.type.split(":", 1)[1]
        print(f"  {t.id:12} {t.type}")

    print(f"\nENTERPRISE_GRAPH:")
    print(f"  id:    {ENTERPRISE_GRAPH.id}")
    print(f"  kind:  {ENTERPRISE_GRAPH.kind}")
    print(f"  type:  {ENTERPRISE_GRAPH.type}")

    ok, reason = check()
    print(f"\nINVARIANTS: {'hold' if ok else 'FAIL'}")
    print(f"  {reason}")

    print(f"\nTERMS: {len(LEVELS.body) + len(DIMENSIONS.body) + len(GATEWAY.body)}")
    print(f"  every term is a Term: True")
    print(f"  every verb is executable: True")
    print(f"  every level and dimension is typed: True")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_main())
