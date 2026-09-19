"""Four endpoints, four assertions. One server for all tests."""
from __future__ import annotations
import json
import sys
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "web"))

from backend import make_server  # noqa: E402

PORT = 8877
TOKEN = "dev-token"
BASE = f"http://127.0.0.1:{PORT}"
_server = None


def setup_module(module):
    global _server
    _server = make_server("127.0.0.1", PORT)
    threading.Thread(target=_server.serve_forever, daemon=True).start()
    time.sleep(0.3)


def teardown_module(module):
    global _server
    if _server is not None:
        _server.shutdown()
        _server.server_close()
        _server = None


def _get(path, token=TOKEN):
    req = urllib.request.Request(BASE + path)
    if token:
        req.add_header("X-Sovereign-Token", token)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_health_ok():
    status, body = _get("/api/health", token=None)
    assert status == 200 and body["ok"] is True


def test_classify_ucI():
    status, body = _get("/api/classify?corpus=mesh/specs_uci")
    assert status == 200 and body["ok"] is True
    assert "BUILDABLE" in body["distribution"]


def test_auth_refuses_without_token():
    status, body = _get("/api/classify?corpus=mesh/specs_uci", token=None)
    assert status == 401
    assert body["error"]["code"] == "auth.missing"


def test_standards_lists_generated():
    status, body = _get("/api/standards")
    assert status == 200 and body["ok"] is True
    assert len(body["generated"]) > 0
