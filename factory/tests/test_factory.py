import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "factory"))
from factory import run, load_blueprint

def test_blueprint_loads():
    bp = load_blueprint("mesh.v1")
    assert bp["blueprint_id"] == "mesh.v1"
    assert len(bp["stages"]) == 6

def test_run_completes():
    r = run("mesh.v1")
    assert r["status"] == "pass"
    for s in r["stages"]:
        assert s["status"] == "ok"

def test_report_written():
    run("mesh.v1")
    assert (ROOT / "factory" / "build" / "factory_report.json").exists()
