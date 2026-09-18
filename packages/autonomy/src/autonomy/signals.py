"""Runtime signals: blast_radius, confidence, human_available.

The evaluator requires these values. A caller that supplies them is
trusted; a caller that does not gets a provider that reports "unknown",
which the evaluator refuses.

The default provider reads:
  - blast_radius: an executable `blast` in PATH that prints a number
  - confidence: a file `security/confidence.signal` with a float
  - human_available: a file `security/human.heartbeat` with a recent timestamp
"""
from __future__ import annotations
import shutil
import subprocess
import time
from pathlib import Path


class Signals:
    def blast_radius(self, action: str) -> int:
        raise NotImplementedError

    def confidence(self, action: str) -> float:
        raise NotImplementedError

    def human_available(self) -> bool:
        raise NotImplementedError


class FilesystemSignals(Signals):
    """Reads signals from the filesystem.

    Missing signals return safe defaults the evaluator will refuse.
    """

    def __init__(self, root: Path):
        self.root = root

    def blast_radius(self, action: str) -> int:
        # Look for a `blast` executable in PATH. It prints a number.
        blast_bin = shutil.which("blast")
        if not blast_bin:
            return -1
        try:
            r = subprocess.run(
                [blast_bin, action], capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0:
                return int(r.stdout.strip())
        except Exception:
            pass
        return -1

    def confidence(self, action: str) -> float:
        p = self.root / "security" / "confidence.signal"
        if not p.exists():
            return 0.0
        try:
            return float(p.read_text().strip())
        except Exception:
            return 0.0

    def human_available(self) -> bool:
        p = self.root / "security" / "human.heartbeat"
        if not p.exists():
            return False
        try:
            last = float(p.read_text().strip())
            return (time.time() - last) < 300  # heartbeat within 5 minutes
        except Exception:
            return False


class StaticSignals(Signals):
    """Test helper. Returns fixed values. Never used in production."""

    def __init__(self, blast_radius=-1, confidence=0.0, human_available=False):
        self._br = blast_radius
        self._c = confidence
        self._h = human_available

    def blast_radius(self, action: str) -> int:
        return self._br

    def confidence(self, action: str) -> float:
        return self._c

    def human_available(self) -> bool:
        return self._h
