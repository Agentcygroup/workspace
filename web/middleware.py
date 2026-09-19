"""Middleware: log, rate limit, CORS, auth, error envelope.

Each function wraps a handler. Composed in backend.py in this order:

    auth -> rate_limit -> cors -> log -> handler

The order matters: an unauthenticated request is refused before it
consumes a rate-limit slot; a rate-limited request is refused before
it reaches the handler. Every refusal uses the same envelope shape:

    {"ok": false, "error": {"code": "...", "reason": "..."}}
"""
from __future__ import annotations
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Request:
    method: str
    path: str
    query: dict
    headers: dict
    body: bytes = b""
    client: str = ""


@dataclass
class Response:
    status: int
    body: bytes
    headers: dict = field(default_factory=dict)

    @classmethod
    def json(cls, status: int, payload: dict, extra: dict | None = None):
        body = json.dumps(payload, indent=2, default=str).encode()
        h = {"Content-Type": "application/json"}
        if extra:
            h.update(extra)
        return cls(status=status, body=body, headers=h)


def error(status: int, code: str, reason: str) -> Response:
    return Response.json(status, {"ok": False,
                                  "error": {"code": code, "reason": reason}})


# --- the middleware chain -------------------------------------------------

TOKENS = {"dev-token"}          # replace with a real source in prod
RATE_WINDOW = 60.0              # seconds
RATE_MAX = 120                  # requests per window per client
_hits: dict[str, list[float]] = defaultdict(list)


def auth(req: Request) -> Response | None:
    """Every request must carry X-Sovereign-Token except /api/health."""
    if req.path == "/api/health":
        return None
    tok = req.headers.get("X-Sovereign-Token", "")
    if tok not in TOKENS:
        return error(401, "auth.missing",
                     "missing or invalid X-Sovereign-Token")
    return None


def rate_limit(req: Request) -> Response | None:
    now = time.time()
    bucket = _hits[req.client]
    _hits[req.client] = [t for t in bucket if now - t < RATE_WINDOW]
    if len(_hits[req.client]) >= RATE_MAX:
        return error(429, "rate.exceeded",
                     f"more than {RATE_MAX} requests in {RATE_WINDOW:.0f}s")
    _hits[req.client].append(now)
    return None


def cors(req: Request) -> Response | None:
    """CORS is not refused here; the header is added on success paths."""
    return None


def log(req: Request) -> Response | None:
    """Log every request to stderr and to standards/http_log.jsonl."""
    line = json.dumps({"at": time.time(),
                       "method": req.method,
                       "path": req.path,
                       "client": req.client})
    from pathlib import Path
    p = Path("standards/http_log.jsonl")
    p.parent.mkdir(exist_ok=True)
    with p.open("a") as f:
        f.write(line + "\n")
    return None


CHAIN = [auth, rate_limit, cors, log]


def run_chain(req: Request) -> Response | None:
    for fn in CHAIN:
        r = fn(req)
        if r is not None:
            return r
    return None
