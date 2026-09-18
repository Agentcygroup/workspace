from heal import Supervisor, ProcessState

def test_register():
    s = Supervisor()
    s.register("a", lambda: None)
    assert "a" in s.processes

def test_run_once_success():
    s = Supervisor()
    s.register("a", lambda: None)
    assert s.run_once("a") is True
    assert s.processes["a"].state == ProcessState.RUNNING

def test_run_once_failure():
    def boom(): raise RuntimeError("x")
    s = Supervisor()
    s.register("a", boom)
    assert s.run_once("a") is False
    assert s.processes["a"].state == ProcessState.FAILED

def test_heal_after_failure():
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] < 2: raise RuntimeError("first fails")
    s = Supervisor()
    s.register("a", flaky, max_attempts=5)
    s.run_once("a")
    assert s.heal("a") is True
    assert s.processes["a"].state == ProcessState.RESTARTED

def test_heal_exhausts_attempts():
    def always_fail(): raise RuntimeError("x")
    s = Supervisor()
    s.register("a", always_fail, max_attempts=2)
    s.run_once("a")
    assert s.heal("a") is False
    assert s.processes["a"].state == ProcessState.STOPPED

def test_history_records():
    s = Supervisor()
    s.register("a", lambda: None)
    s.run_once("a")
    assert len(s.history) == 1
