import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from homeostasis import ALL_DRIVES, DriveVector, Refusal, evaluate
from homeostasis.regulate import regulate


def _low_state():
    dv = DriveVector()
    for d in ALL_DRIVES:
        dv.set(d, 0.1)
    return dv


def _target():
    dv = DriveVector()
    for d in ALL_DRIVES:
        dv.set(d, 0.95)
    return dv


def test_converges_to_admissible_setpoint():
    r = regulate(_low_state(), _target(), epsilon=0.02, step_size=0.2, max_steps=100)
    assert r.converged is True
    assert evaluate(r.final).allow is True


def test_records_every_step():
    r = regulate(_low_state(), _target(), epsilon=0.02, step_size=0.2, max_steps=100)
    assert len(r.trace.steps) > 0
    for drive, before, after in r.trace.steps:
        assert drive in ALL_DRIVES
        assert 0.0 <= before <= 1.0
        assert 0.0 <= after <= 1.0


def test_inadmissible_setpoint_refused():
    sp = _target()
    sp.set("truth", 0.5)
    try:
        regulate(_low_state(), sp)
        assert False
    except Refusal as e:
        assert "inadmissible" in e.code


def test_missing_state_drive_refused():
    dv = DriveVector()
    dv.set(ALL_DRIVES[0], 1.0)
    try:
        regulate(dv, _target())
        assert False
    except Refusal as e:
        assert "missing" in e.code


def test_budget_exhausted_returns_not_converged():
    r = regulate(_low_state(), _target(), epsilon=0.001, step_size=0.01, max_steps=5)
    assert r.converged is False
    assert r.trace.terminal == "budget-exhausted"


def test_greedy_picks_largest_error():
    state = DriveVector()
    for d in ALL_DRIVES:
        state.set(d, 0.9)
    state.set("truth", 0.0)
    r = regulate(state, _target(), epsilon=0.02, step_size=0.2, max_steps=100)
    assert r.trace.steps[0][0] == "truth"


def test_final_state_admissible_after_convergence():
    r = regulate(_low_state(), _target(), epsilon=0.02, step_size=0.2, max_steps=200)
    if r.converged:
        assert evaluate(r.final).allow is True


def test_step_size_clamped_at_bounds():
    r = regulate(_low_state(), _target(), epsilon=0.02, step_size=0.5, max_steps=10)
    for _, _, after in r.trace.steps:
        assert 0.0 <= after <= 1.0


def main() -> int:
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    ok = fail = 0
    for t in tests:
        try:
            t()
            print(f"  {t.__name__:55} ok")
            ok += 1
        except AssertionError as e:
            print(f"  {t.__name__:55} FAIL {e}")
            fail += 1
        except Refusal as e:
            print(f"  {t.__name__:55} FAIL refusal {e.code}")
            fail += 1
    print(f"\n{ok} ok, {fail} fail")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
