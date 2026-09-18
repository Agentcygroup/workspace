import pytest
from hle import (
    LEADERBOARD, NON_IMPLICATION,
    claim_hle_passing_is_real,
    claim_hle_passing_is_not_agi,
    claim_agi_has_no_benchmark,
    guard, AGIRefusal,
    harness, compare_to_leaderboard,
)
from hle.schema import build_all


def test_leaderboard_nonempty():
    assert len(LEADERBOARD) >= 10
    assert "Gemini 3 Pro" in LEADERBOARD
    assert LEADERBOARD["Gemini 3 Pro"]["accuracy"] == 38.3


def test_claim_1_real():
    c = claim_hle_passing_is_real()
    assert c["claim"].startswith("HLE passing is a defined")
    assert c["grounding"]["question_count"] == 2500
    assert c["status"] == "supported"


def test_claim_2_not_agi():
    c = claim_hle_passing_is_not_agi()
    assert "not alone suggest" in c["grounding"]["quote"]
    assert c["status"] == "supported_by_source"


def test_claim_3_no_agi_benchmark():
    c = claim_agi_has_no_benchmark()
    assert c["grounding"]["no_agi_benchmark_exists"] is True
    assert c["status"] == "supported_by_absence_of_counterexample"


def test_guard_rejects_agi_claim():
    with pytest.raises(AGIRefusal):
        guard("Our system is AGI.")
    with pytest.raises(AGIRefusal):
        guard("We passed HLE therefore AGI.")


def test_guard_accepts_honest_text():
    assert guard("HLE passing is a real achievement. It is not AGI.") is True


def test_harness_runs_on_small_set():
    qs = [
        {"id": "1", "subject": "math", "question": "2+2?", "answer": "4"},
        {"id": "2", "subject": "math", "question": "3+3?", "answer": "6"},
        {"id": "3", "subject": "bio",  "question": "?",     "answer": "x"},
    ]
    def answer_fn(q):
        return {"1": "4", "2": "6", "3": "wrong"}.get(q["id"], "")
    r = harness(qs, answer_fn)
    assert r["total"] == 3
    assert r["correct"] == 2
    assert r["accuracy"] == pytest.approx(66.67, abs=0.01)
    assert r["by_subject"]["math"]["correct"] == 2
    assert r["by_subject"]["bio"]["correct"] == 0


def test_harness_report_carries_refusal():
    r = harness([{"id":"1","subject":"x","question":"?","answer":"a"}], lambda q: "a")
    assert "AGI" in r["refuses_to_claim"]
    assert r["non_implication"] == NON_IMPLICATION


def test_harness_report_forbidden_token_would_raise():
    # if answer_fn returns text containing an AGI claim, guard fires at report time
    def fn(q):
        return "we are agi"
    # this is fine because report text is only accuracy; guard checks report not answers
    r = harness([{"id":"1","subject":"x","question":"?","answer":"we are agi"}], fn)
    assert r["correct"] == 1


def test_compare_to_leaderboard():
    r = {"accuracy": 38.0}
    c = compare_to_leaderboard(r)
    assert c["closest_entry"] == "Gemini 3 Pro"
    assert c["delta"] < 1.0
    assert c["context_only"] is True


def test_build_all(tmp_path):
    written = build_all(tmp_path)
    assert any("leaderboard" in w for w in written)
    assert any("claim_1_real" in w for w in written)
    assert any("claim_2_not_agi" in w for w in written)
    assert any("claim_3_no_agi_benchmark" in w for w in written)
    assert any("non_implication" in w for w in written)


def test_assertions_closed_set():
    from hle import ASSERTIONS
    assert len(ASSERTIONS) >= 5
    assert "is agi" in ASSERTIONS
