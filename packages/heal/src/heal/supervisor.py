import time
from dataclasses import dataclass, field

class ProcessState:
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    RESTARTED = "restarted"
    STOPPED = "stopped"

@dataclass
class Process:
    name: str
    fn: callable
    state: str = ProcessState.PENDING
    attempts: int = 0
    max_attempts: int = 3
    last_error: str = ""

@dataclass
class Supervisor:
    processes: dict = field(default_factory=dict)
    history: list = field(default_factory=list)

    def register(self, name, fn, max_attempts=3):
        p = Process(name, fn, max_attempts=max_attempts)
        self.processes[name] = p
        return p

    def run_once(self, name):
        p = self.processes.get(name)
        if p is None:
            raise KeyError("unknown process: " + name)
        p.attempts += 1
        try:
            p.fn()
            p.state = ProcessState.RUNNING
            p.last_error = ""
            self.history.append({"name": name, "result": "ok", "attempt": p.attempts})
            return True
        except Exception as e:
            p.state = ProcessState.FAILED
            p.last_error = str(e)
            self.history.append({"name": name, "result": "fail", "attempt": p.attempts, "error": str(e)})
            return False

    def heal(self, name):
        p = self.processes[name]
        while p.attempts < p.max_attempts:
            ok = self.run_once(name)
            if ok:
                p.state = ProcessState.RESTARTED
                return True
        p.state = ProcessState.STOPPED
        return False

    def run_all(self):
        results = {}
        for name in self.processes:
            if not self.run_once(name):
                results[name] = self.heal(name)
            else:
                results[name] = True
        return results
