import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "mesh"))
from mesh import run, load_specs
from kinds import engine_for, DECLARATIVE_LEVELS
from kinds.engine_record import emit as emit_record

def test_specs_dir_exists():
    assert (ROOT / "mesh" / "specs").exists()

def test_engine_for_declarative():
    spec = {"kind_id":"REGISTRY-ENTRY","level":"REGISTRY","name":"ENTRY","status":"specified"}
    assert engine_for(spec) is not None

def test_engine_for_stub_returns_none():
    spec = {"kind_id":"ISA-NOP","level":"INSTRUCTION_SET_ARCHITECTURE","name":"NOP","status":"stub"}
    assert engine_for(spec) is None

def test_record_emits_file(tmp_path):
    spec = {"kind_id":"REGISTRY-ENTRY","level":"REGISTRY","name":"ENTRY","status":"specified"}
    files = emit_record(spec, tmp_path)
    assert len(files) == 1
    assert Path(files[0]).exists()

def test_run_writes_report():
    report = run()
    assert (ROOT / "mesh" / "report.json").exists()
