"""Backend: routes over http.server.

Routes:
  GET  /api/health                 liveness, no auth
  GET  /api/classify?corpus=...    classifier distribution for a corpus
  POST /api/pipe                   run pipe/autonomous_pipe.py, return JSON
  GET  /api/standards              read standards/INDEX.json

Each handler returns a Response. The chain in middleware.py runs before
the handler. Nothing is served that the chain hasn't passed.
"""
from __future__ import annotations
import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))
sys.path.insert(0, str(HERE))

from middleware import Request, Response, error, run_chain  # noqa: E402


def _run(cmd, cwd=ROOT, timeout=120):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True,
                           text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def handle_health(_req: Request) -> Response:
    return Response.json(200, {"ok": True, "service": "sovereign",
                               "version": "0.1.0"})


def handle_classify(req: Request) -> Response:
    corpus = req.query.get("corpus", ["mesh/specs_uci"])[0]
    target = ROOT / corpus
    if not target.exists():
        return error(404, "corpus.missing", f"{corpus} not found")
    rc, out, err = _run(
        [sys.executable, "-m", "buildability.classify", str(target)],
        cwd=str(ROOT / "packages" / "buildability" / "src"),
    )
    if rc != 0:
        return error(500, "classify.failed", err[-400:] or "unknown")
    lines = out.strip().splitlines()
    dist: dict[str, int] = {}
    in_dist = False
    for line in lines:
        if line.startswith("distribution:"):
            in_dist = True
            continue
        if in_dist and line.strip():
            parts = line.strip().split()
            if len(parts) >= 2:
                dist[parts[0]] = int(parts[-1])
    return Response.json(200, {"ok": True, "corpus": corpus,
                               "distribution": dist,
                               "lines": len(lines)})


def handle_pipe(_req: Request) -> Response:
    rc, out, err = _run([sys.executable, str(ROOT / "pipe" / "autonomous_pipe.py")],
                        timeout=300)
    outcome = ROOT / "pipe" / "outcome.json"
    if not outcome.exists():
        return error(500, "pipe.no_outcome", err[-400:] or "outcome missing")
    d = json.loads(outcome.read_text())
    return Response.json(200, {"ok": True, "passed": d.get("passed"),
                               "stages": d.get("stages", [])})


def handle_standards(_req: Request) -> Response:
    idx = ROOT / "standards" / "INDEX.json"
    if not idx.exists():
        return error(404, "standards.missing", "standards/INDEX.json absent")
    d = json.loads(idx.read_text())
    return Response.json(200, {"ok": True,
                               "generated": d.get("generated", []),
                               "omitted": d.get("omitted_or_error", [])})


ROUTES = {
    ("GET", "/api/health"):    handle_health,
    ("GET", "/api/classify"):  handle_classify,
    ("POST", "/api/pipe"):     handle_pipe,
    ("GET", "/api/standards"): handle_standards,
}


class Handler(BaseHTTPRequestHandler):
    def _dispatch(self):
        url = urlparse(self.path)
        path = url.path
        method = self.command
        query = parse_qs(url.query)
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b""
        req = Request(method=method, path=path, query=query,
                      headers={k: v for k, v in self.headers.items()},
                      body=body, client=self.client_address[0])
        refusal = run_chain(req)
        if refusal is not None:
            self._respond(refusal)
            return
        handler = ROUTES.get((method, path))
        if handler is None:
            self._respond(error(404, "route.unknown",
                                f"{method} {path}"))
            return
        try:
            self._respond(handler(req))
        except Exception as e:
            self._respond(error(500, "handler.raised", f"{type(e).__name__}: {e}"))

    def _respond(self, resp: Response):
        self.send_response(resp.status)
        for k, v in resp.headers.items():
            self.send_header(k, v)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(resp.body)))
        self.end_headers()
        self.wfile.write(resp.body)

    def do_GET(self):
        self._dispatch()

    def do_POST(self):
        self._dispatch()

    def log_message(self, *args):
        pass


def make_server(host="127.0.0.1", port=8765):
    from http.server import HTTPServer
    return HTTPServer((host, port), Handler)
