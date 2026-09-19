"""Kernel self-test. Runs on __main__. Every assertion is real."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from substrate import (
    Term, Refusal, PRIMITIVES, CONSTRUCTORS, DERIVED, VOCABULARY,
    atom, compose, product, sum, quote, derive, admits, lookup,
    collection, subset, relation, function, state, transformation,
    observation, evidence, proof, counterexample, validator, execution,
    policy, certificate, description, axiom, principle, invariant,
    constraint, grammar, format, structure,
)


def test_nine_primitives():
    assert len(PRIMITIVES) == 9
    assert "unit" in PRIMITIVES and "ref" in PRIMITIVES


def test_six_constructors():
    assert len(CONSTRUCTORS) == 6


def test_atom_rejects_unknown_kind():
    try:
        atom("frobnitz", 1)
        assert False, "should have refused"
    except Refusal as e:
        assert e.code == "substrate.unknown.frobnitz"


def test_atom_checks_value():
    try:
        atom("nat", -1)
        assert False, "should have refused"
    except Refusal as e:
        assert e.code == "substrate.atom.bad-value.nat"


def test_every_primitive_constructs():
    a = atom("name", "x")
    assert a.kind == "name"
    assert atom("bool", True).body is True
    assert atom("nat", 7).body == 7
    assert atom("unit", None).kind == "unit"


def test_compose_chains():
    inc = atom("fn", lambda x: x + 1)
    dbl = atom("fn", lambda x: x * 2)
    chained = compose(inc, dbl)
    assert chained.body(3) == 7  # (3*2)+1


def test_compose_refuses_non_fn():
    a = atom("name", "x")
    try:
        compose(a, a)
        assert False
    except Refusal as e:
        assert e.code == "substrate.compose.not-fn"


def test_collection_and_subset():
    xs = collection(atom("nat", 1), atom("nat", 2), atom("nat", 3))
    even = atom("fn", lambda t: t.body % 2 == 0)
    ys = subset(xs, even)
    assert len(ys.body) == 1


def test_proof_needs_derivation():
    c = axiom("x=x")
    try:
        proof(c, ())
        assert False
    except Refusal as e:
        assert e.code == "substrate.proof.empty-derivation"


def test_evidence_is_a_product():
    claim = axiom("all ravens are black")
    witness = atom("name", "raven_001")
    e = evidence(claim, witness)
    assert e.kind == "pair"


def test_counterexample_records_claim_and_witness():
    claim = axiom("all swans are white")
    witness = atom("name", "black_swan")
    c = counterexample(claim, witness)
    assert c.body["claim"] == {"name": "all swans are white"}
    assert c.body["witness"] == "black_swan"


def test_validator_uses_predicate():
    claim = axiom("x > 0")
    pred = atom("fn", lambda w: w > 0)
    v = validator(claim, pred)
    assert v.body(1) is True
    assert v.body(-1) is False


def test_execution_runs_fn():
    inc = atom("fn", lambda x: x + 1)
    arg = atom("nat", 5)
    e = execution(inc, arg)
    assert e.body["result"] == 6


def test_policy_refuses_non_fn_action():
    claim = axiom("y")
    pred = atom("fn", lambda x: True)
    not_fn = atom("name", "no")
    try:
        policy("p", pred, not_fn)
        assert False
    except Refusal as e:
        assert e.code == "substrate.policy.not-fn"


def test_certificate_names_subject_and_issuer():
    s = axiom("health")
    c = proof(s, (("by", "assumption"),))
    cert = certificate(s, c, "kernel")
    assert cert.body["issuer"] == "kernel"


def test_grammar_and_format():
    g = grammar("spec", (("Spec", ("Component", "Interface")),))
    f = format("component", ("name", "responsibility"))
    assert g.body["name"] == "spec"
    assert f.body["fields"] == ("name", "responsibility")


def test_recursive_closure():
    """Every name in VOCABULARY can be referenced as a Term."""
    for name in PRIMITIVES:
        assert lookup(name) is not None
        assert admits(name)
    for name in DERIVED:
        assert admits(name)
        assert lookup(name) is not None


def test_unknown_name_is_refused():
    assert not admits("frobnitz")
    assert lookup("frobnitz") is None


def test_quote_returns_a_term_of_a_term():
    x = atom("name", "x")
    q = quote(x)
    assert q.body is x


def test_derive_appends_a_rule():
    x = atom("name", "x")
    y = derive(x, "by-introduction")
    assert ("derive", "by-introduction") in y.derivation


def test_no_semantic_escape():
    """Everything constructible is a Term. There is no second shape."""
    made = [
        atom("name", "x"),
        atom("fn", lambda v: v),
        collection(atom("nat", 1), atom("nat", 2)),
    ]
    g = atom("fn", lambda t: t.body % 2 == 0)
    made.append(subset(made[2], g))
    made.append(proof(axiom("p"), (("rule",),)))
    made.append(certificate(made[-1], proof(axiom("q"), (("rule",),)), "me"))
    for m in made:
        assert isinstance(m, Term)
        assert isinstance(m.id, str)
        assert isinstance(m.kind, str)
        assert isinstance(m.derivation, tuple)


def main() -> int:
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    ok = 0
    fail = 0
    for t in tests:
        try:
            t()
            print(f"  {t.__name__:55} ok")
            ok += 1
        except AssertionError as e:
            print(f"  {t.__name__:55} FAIL {e}")
            fail += 1
        except Refusal as e:
            print(f"  {t.__name__:55} FAIL refusal {e.code}")
            fail += 1
    print(f"\n{ok} ok, {fail} fail")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
