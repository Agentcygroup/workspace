import json
import pytest
from pathlib import Path
from taxonomy import LEVELS, KINDS, INVARIANTS, level_of, is_kind, scan_forbidden
from taxonomy.schema import schema_for, validate_instance

def test_levels_closed():
    assert len(LEVELS) == 16
    assert LEVELS[0] == "PHYSICAL"
    assert LEVELS[5] == "INSTRUCTION_SET_ARCHITECTURE"
    assert LEVELS[15] == "META"

def test_opcodes_present():
    assert is_kind("INSTRUCTION_SET_ARCHITECTURE", "NOP")
    assert is_kind("INSTRUCTION_SET_ARCHITECTURE", "CALL")
    assert not is_kind("INSTRUCTION_SET_ARCHITECTURE", "FORK")

def test_syscalls_present():
    assert is_kind("OPERATING_SYSTEM", "FORK")
    assert is_kind("OPERATING_SYSTEM", "SECCOMP")

def test_scan_forbidden():
    hits = scan_forbidden({"note": "this is complete"})
    assert any("complete" in t for _, t in hits)
    hits2 = scan_forbidden({"scoped": True, "level": "LEDGER", "kind": "CLAIM"})
    assert hits2 == []

def test_validate_instance_ok():
    inst = {"level": "LEDGER", "kind": "CLAIM", "scoped": True,
            "bound": "sources.v1.0.0", "version": "1.0.0"}
    lvl, ok, reasons = validate_instance(inst)
    assert lvl == "LEDGER" and ok and reasons == []

def test_validate_instance_bad_kind():
    inst = {"level": "LEDGER", "kind": "NOP", "scoped": True}
    lvl, ok, reasons = validate_instance(inst)
    assert lvl == "LEDGER" and not ok
    assert any("not in level" in r for r in reasons)

def test_validate_instance_unscoped():
    inst = {"level": "LEDGER", "kind": "CLAIM", "scoped": False}
    lvl, ok, reasons = validate_instance(inst)
    assert not ok
    assert any("scoped" in r for r in reasons)

def test_schema_for_level():
    s = schema_for("OPERATING_SYSTEM")
    assert s["properties"]["kind"]["enum"] == KINDS["OPERATING_SYSTEM"]
    assert s["properties"]["level"]["const"] == "OPERATING_SYSTEM"

def test_invariants_closed():
    assert len(INVARIANTS) == 15
    assert "NO_LEVEL_CLAIMS_UNSCOPED_COMPLETENESS" in INVARIANTS
