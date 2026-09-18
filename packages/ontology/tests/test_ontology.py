from ontology import LEVELS, KIND_INDEX, BINDS, INVARIANTS, validate, gap_register, implementation_status

def test_sixteen_levels():
    assert len(LEVELS) == 16

def test_validate_clean():
    assert validate() == []

def test_binds_chain():
    assert len(BINDS) == 17
    assert ("PHYSICAL","GATE") in BINDS
    assert ("META","PHYSICAL") in BINDS

def test_fifteen_invariants():
    assert len(INVARIANTS) == 15

def test_isa_opcodes_count():
    assert len(KIND_INDEX["INSTRUCTION_SET_ARCHITECTURE"]) == 50

def test_syscall_count():
    assert len(KIND_INDEX["OPERATING_SYSTEM"]) == 53

def test_asm_directives_count():
    assert len(KIND_INDEX["ASSEMBLY"]) == 38

def test_hll_constructs_count():
    assert len(KIND_INDEX["HIGH_LEVEL_LANGUAGE"]) == 51

def test_app_types_count():
    assert len(KIND_INDEX["APPLICATION"]) == 49

def test_framework_kinds_count():
    assert len(KIND_INDEX["FRAMEWORK"]) == 35

def test_registry_kinds_count():
    assert len(KIND_INDEX["REGISTRY"]) == 24

def test_ledger_kinds_count():
    assert len(KIND_INDEX["LEDGER"]) == 25

def test_artifact_kinds_count():
    assert len(KIND_INDEX["ARTIFACT"]) == 24

def test_governance_kinds_count():
    assert len(KIND_INDEX["GOVERNANCE"]) == 32

def test_meta_kinds_count():
    assert len(KIND_INDEX["META"]) == 35

def test_gap_register_nonempty():
    g = gap_register()
    assert len(g) > 200

def test_implementation_status():
    s = implementation_status()
    assert s["INSTRUCTION_SET_ARCHITECTURE"]["implemented"] == 0
    assert s["REGISTRY"]["implemented"] == 5
    assert s["LEDGER"]["implemented"] == 4
    assert s["ARTIFACT"]["implemented"] == 6
