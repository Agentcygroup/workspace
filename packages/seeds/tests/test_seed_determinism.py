"""Determinism test for the seed graph."""
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def test_seed_stats_are_deterministic():
    """Two consecutive runs of the seed seeder produce identical output."""
    def run():
        r = subprocess.run(
            ["python", "packages/seeds/seeds.py", "--stats"],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
        return r.stdout
    a, b = run(), run()
    assert a == b, "seed stats differ across runs"
