from agent_data import analyze, evidence, run
import json
from pathlib import Path

CSV = "id,name,amount\n1,alice,10.5\n2,bob,\n3,carol,20.0\n"

def test_analyze_schema():
    a = analyze(CSV)
    assert a["schema"] == ["id","name","amount"]
    assert a["row_count"] == 3

def test_empty_column_detected():
    a = analyze(CSV)
    amount = next(c for c in a["columns"] if c["column"] == "amount")
    assert amount["empty"] == 1
    assert amount["numeric_parseable"] == 2
    assert amount["min"] == 10.5
    assert amount["max"] == 20.0

def test_source_hash_stable():
    a1 = analyze(CSV)
    a2 = analyze(CSV)
    assert a1["source_sha256"] == a2["source_sha256"]

def test_evidence_scoped():
    ev = evidence(analyze(CSV))
    assert ev["scoped"] is True
    assert ev["kind"] == "evidence"
    assert ev["level"] == "LEDGER"

def test_run_writes(tmp_path):
    i = tmp_path / "in.csv"; i.write_text(CSV)
    o = tmp_path / "out.json"
    run(str(i), str(o))
    data = json.loads(o.read_text())
    assert data["payload"]["row_count"] == 3
