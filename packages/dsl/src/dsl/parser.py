from dataclasses import dataclass, field
from .lexer import Token

class ParseError(Exception): pass

@dataclass
class Step:
    name: str
    op: str
    args: list = field(default_factory=list)

@dataclass
class Program:
    name: str
    steps: list = field(default_factory=list)

class _P:
    def __init__(self, tokens): self.t = tokens; self.i = 0
    def peek(self): return self.t[self.i] if self.i < len(self.t) else None
    def eat(self, kind=None, value=None):
        tok = self.peek()
        if tok is None: raise ParseError("unexpected eof")
        if kind and tok.kind != kind: raise ParseError(f"expected {kind}, got {tok.kind}")
        if value and tok.value != value: raise ParseError(f"expected {value}, got {tok.value}")
        self.i += 1
        return tok

def parse(tokens):
    p = _P(tokens)
    p.eat("KW", "braid")
    name = p.eat("IDENT").value
    p.eat("{")
    prog = Program(name)
    while True:
        tok = p.peek()
        if tok is None: raise ParseError("missing }")
        if tok.kind == "}": p.eat("}"); break
        p.eat("KW", "step")
        sname = p.eat("IDENT").value
        p.eat(":")
        op = p.eat("IDENT").value
        args = []
        while p.peek() and p.peek().kind in ("STRING","IDENT"):
            args.append(p.eat(p.peek().kind).value)
        prog.steps.append(Step(sname, op, args))
    return prog
