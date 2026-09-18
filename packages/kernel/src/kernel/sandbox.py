"""Sandbox: signature, lint, version pin, resource limit, timeout."""
__version__ = "0.1.0"
import hashlib
import json
import signal
import time
from typing import Any, Callable

class SandboxRejection(Exception):
    pass

ALLOWED_OPERATORS = ["id","neg","count","merge","split","filter","map","fold","align","project"]
MAX_PAYLOAD_BYTES = 1_000_000
MAX_RUNTIME_SECONDS = 5

def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()

def _sign(payload):
    return hashlib.sha256(_canon(payload)).hexdigest()

def _lint(op_name, args):
    if op_name not in ALLOWED_OPERATORS:
        raise SandboxRejection("operator not allowed: " + op_name)
    size = len(_canon(args))
    if size > MAX_PAYLOAD_BYTES:
        raise SandboxRejection(f"payload too large: {size} > {MAX_PAYLOAD_BYTES}")

def _timeout_handler(signum, frame):
    raise SandboxRejection("sandbox timeout")

def run_in_sandbox(op_name, args, signature_expected=None, fn: Callable = None):
    if fn is None:
        from .operators import OPERATORS
        fn = OPERATORS[op_name]["fn"] if op_name in OPERATORS else None
        if fn is None:
            raise SandboxRejection("unknown operator: " + op_name)
    _lint(op_name, args)
    sig = _sign({"op": op_name, "args": args})
    if signature_expected and sig != signature_expected:
        raise SandboxRejection("signature mismatch")
    old = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(MAX_RUNTIME_SECONDS)
    start = time.time()
    try:
        result = fn(*args) if isinstance(args, tuple) else fn(args)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
    elapsed = time.time() - start
    return {"result": result, "signature": _sign({"op": op_name, "args": args, "out": result}), "elapsed": elapsed}
