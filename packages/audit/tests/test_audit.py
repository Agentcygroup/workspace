import pytest
from audit import AuditLog, AuditEvent
from ledger import ChainError

def test_append_event():
    log = AuditLog()
    log.append(AuditEvent("alice","read","file","ok"))
    assert log.count() == 1

def test_verify_clean():
    log = AuditLog()
    log.append(AuditEvent("a","b","c","ok"))
    assert log.verify()

def test_tamper_detected():
    log = AuditLog()
    log.append(AuditEvent("a","b","c","ok"))
    log.chain.entries[0]["payload"]["actor"] = "eve"
    with pytest.raises(ChainError):
        log.verify()

def test_save_load(tmp_path):
    log = AuditLog()
    log.append(AuditEvent("a","b","c","ok"))
    p = tmp_path / "audit.json"
    log.save(p)
    log2 = AuditLog.load(p)
    assert log2.count() == 1

def test_non_implication_carried():
    log = AuditLog()
    log.append(AuditEvent("a","b","c","ok","nothing implies recognition"))
    assert "nothing implies recognition" in log.chain.entries[0]["payload"]["non_implication"]
