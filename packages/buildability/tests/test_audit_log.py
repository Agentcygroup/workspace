import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability.audit import record, query


def test_record_appends(tmp_path):
    p = tmp_path / "log.jsonl"
    record("X", "BUILDABLE", path=p)
    record("Y", "RESEARCH", path=p)
    lines = p.read_text().strip().splitlines()
    assert len(lines) == 2
    e0 = json.loads(lines[0])
    assert e0["spec"] == "X" and e0["regime"]


def test_query_filters_by_regime(tmp_path):
    p = tmp_path / "log.jsonl"
    record("X", "BUILDABLE", path=p)
    record("Y", "RESEARCH", path=p)
    record("Z", "BUILDABLE", path=p)
    b = query(regime="BUILDABLE", path=p)
    assert len(b) == 2
    assert {e["spec"] for e in b} == {"X", "Z"}
