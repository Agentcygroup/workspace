class InterpError(Exception): pass

def evaluate(program, handlers):
    ctx = {}
    for s in program.steps:
        fn = handlers.get(s.op)
        if fn is None:
            raise InterpError("unknown op: " + s.op)
        ctx[s.name] = fn(ctx, *s.args)
    return ctx
