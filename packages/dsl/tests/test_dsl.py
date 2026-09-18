import pytest
from dsl import tokenize, parse, evaluate, LexError, ParseError, InterpError

SRC = '''
braid demo {
  step a: load "x"
  step b: wrap a
  step c: emit
}
'''

def test_tokenize_basic():
    toks = tokenize(SRC)
    assert toks[0].value == "braid"
    assert any(t.kind == "STRING" and t.value == "x" for t in toks)

def test_comment_skipped():
    toks = tokenize("# hi\nbraid x { }")
    assert toks[0].value == "braid"

def test_parse_program():
    p = parse(tokenize(SRC))
    assert p.name == "demo"
    assert len(p.steps) == 3
    assert p.steps[0].op == "load"

def test_parse_missing_brace():
    with pytest.raises(ParseError):
        parse(tokenize("braid x {"))

def test_evaluate():
    p = parse(tokenize(SRC))
    handlers = {
        "load": lambda c, v: v,
        "wrap": lambda c, n: "[" + c[n] + "]",
        "emit": lambda c: c["b"] + "!",
    }
    ctx = evaluate(p, handlers)
    assert ctx["c"] == "[x]!"

def test_unknown_op():
    p = parse(tokenize("braid x { step a: nope }"))
    with pytest.raises(InterpError):
        evaluate(p, {})

def test_lex_error():
    with pytest.raises(LexError):
        tokenize("braid x { step a: @ }")
