import json
from ax import (AX, SCOPES, FUNCTIONS, allocation_for, categories,
                agent_capable, human_required, coverage, scope_variants)
from ax.schema import build_all, schema

def test_all_42_categories():
    assert len(AX) == 42
    assert len(categories()) == 42

def test_coverage_sums_to_42():
    assert sum(coverage().values()) == 42

def test_every_allocation_legal():
    legal = {"human_only","assisted","human_approved","human_supervised",
             "exception_supervised","dual_control","agent_executed",
             "machine_executed","multi_agent","prohibited"}
    for cat, e in AX.items():
        assert e["allocation"] in legal, cat

def test_software_is_agent_executed():
    assert allocation_for("5_software_engineering") == "agent_executed"

def test_legal_is_human_only():
    assert allocation_for("20_legal_regulatory_ip") == "human_only"

def test_agent_capable_lists():
    caps = agent_capable("5_software_engineering")
    assert "software_engineer" in caps

def test_human_required_lists():
    hum = human_required("10_cybersecurity")
    assert "ciso" in hum

def test_scope_variants_15x26():
    v = scope_variants("security_architect")
    assert len(v) == len(SCOPES) * len(FUNCTIONS)
    assert len(v) == len(SCOPES) * len(FUNCTIONS)

def test_schema_enum():
    s = schema()
    assert "agent_executed" in s["properties"]["allocation"]["enum"]

def test_build_all(tmp_path):
    written = build_all(tmp_path)
    assert any("ax.json" in w for w in written)
    assert any("role_scope_function_grid" in w for w in written)
    ax = json.loads((tmp_path / "ax.json").read_text())
    assert len(ax) == 42
    grid = json.loads((tmp_path / "role_scope_function_grid.json").read_text())
    assert len(grid) > 0
    for row in grid[:10]:
        assert row["scope"] in SCOPES
        assert row["function"] in FUNCTIONS
