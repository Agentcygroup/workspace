import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "autonomy" / "src"))

from autonomy import load_contract, evaluate
from autonomy.evaluator import Action, Context
from autonomy.coordinate import two_phase_commit


def _contract():
    return load_contract(ROOT / "security" / "autonomy_contract.yaml")


def test_both_allowed_commits():
    c = _contract()
    a = Action("detect", "ops", "low")
    r = two_phase_commit(a, a, Context(), Context(), c)
    assert r.committed is True


def test_one_refused_aborts():
    c = _contract()
    ok = Action("detect", "ops", "low")
    bad = Action("report", "org", "medium")
    r = two_phase_commit(ok, bad, Context(), Context(), c)
    assert r.committed is False
    assert "b:" in r.reason
