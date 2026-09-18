import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))
from buildability.crawl import fetch


def test_fetch_unreachable_returns_dict():
    r = fetch("http://127.0.0.1:1/", timeout=1.0)
    assert r["ok"] is False
    assert "reason" in r
