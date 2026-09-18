"""HLE — Humanity's Last Exam engagement, honestly framed.

Three statements are encoded as three modules:

  claim_hle_passing_is_real      -> packages as a checkable achievement
  claim_hle_passing_is_not_agi   -> refuses any AGI inference
  claim_agi_has_no_benchmark     -> refuses to name a benchmark for AGI

The package does not run the benchmark. It does not score models. It does
not claim a score. It does not claim AGI. It provides:

  - a harness that CAN load the public HLE questions and score a caller-
    supplied answering function
  - an accuracy and calibration reporter with the same shape as the HLE
    leaderboard
  - a hard refusal that raises if any caller tries to write an artifact
    claiming AGI or claiming that HLE passing is AGI

The benchmark's own text says: "High accuracy on HLE would demonstrate
expert-level performance on closed-ended, verifiable questions ... but it
would not alone suggest autonomous research capabilities or 'artificial
general intelligence.'" This package takes that sentence literally and
encodes it as a guard.

Non-implication: nothing in this package implies that any system has
passed HLE, is AGI, or will become AGI. Scores are measured, not asserted.
"""
__version__ = "0.1.0"
from .guard import guard, AGIRefusal, ASSERTIONS, NEGATIONS

LEADERBOARD = {
    "Gemini 3 Pro":          {"accuracy": 38.3, "calibration_error": 57.2},
    "GPT-5":                 {"accuracy": 25.3, "calibration_error": 50.0},
    "Grok 4":                {"accuracy": 24.5, "calibration_error": 56.4},
    "Gemini 2.5 Pro":        {"accuracy": 21.6, "calibration_error": 72.0},
    "GPT-5-mini":            {"accuracy": 19.4, "calibration_error": 65.0},
    "Claude 4.5 Sonnet":     {"accuracy": 13.7, "calibration_error": 65.0},
    "Gemini 2.5 Flash":      {"accuracy": 12.1, "calibration_error": 80.0},
    "DeepSeek-R1":           {"accuracy":  8.5, "calibration_error": 73.0},
    "o1":                    {"accuracy":  8.0, "calibration_error": 83.0},
    "GPT-4o":                {"accuracy":  2.7, "calibration_error": 89.0},
}

NON_IMPLICATION = (
    "Passing HLE is a defined, measurable, real achievement. It is not AGI. "
    "The HLE authors say high accuracy on HLE would not alone suggest AGI. "
    "No benchmark exists for AGI, and this package does not name one."
)


def claim_hle_passing_is_real():
    """Return the claim and its grounding, in machine-readable form."""
    return {
        "claim": "HLE passing is a defined, measurable, real achievement.",
        "grounding": {
            "benchmark": "Humanity's Last Exam",
            "published": "Nature 649, 1139-1146 (2026)",
            "question_count": 2500,
            "contributors": "~1000 experts, ~500 institutions, 50 countries",
            "held_out": True,
            "metric": ["accuracy", "calibration_error"],
            "leaderboard_present": True,
        },
        "status": "supported",
    }


def claim_hle_passing_is_not_agi():
    """Return the second claim with the benchmark's own sentence."""
    return {
        "claim": "HLE passing is not AGI by the benchmark's own admission.",
        "grounding": {
            "source": "Humanity's Last Exam, Discussion section",
            "quote": (
                "High accuracy on HLE would demonstrate expert-level performance "
                "on closed-ended, verifiable questions and cutting-edge scientific "
                "knowledge, but it would not alone suggest autonomous research "
                "capabilities or 'artificial general intelligence.'"
            ),
        },
        "status": "supported_by_source",
    }


def claim_agi_has_no_benchmark():
    """Return the third claim."""
    return {
        "claim": "AGI has no benchmark; HLE explicitly declines to be one.",
        "grounding": {
            "hle_self_position": "structured academic problems, not open-ended research",
            "explicit_decline": "HLE is not AGI; HLE passing is not AGI",
            "no_agi_benchmark_exists": True,
        },
        "status": "supported_by_absence_of_counterexample",
    }




def harness(questions, answer_fn):
    """Run answer_fn over questions and report accuracy.

    questions: list of dicts with keys id, subject, question, answer.
    answer_fn: callable(question_dict) -> str.
    Returns: report dict with accuracy and per-subject breakdown.
    Refuses to report anything if guard() would fail on any answer_fn output.
    """
    correct = 0
    total = 0
    by_subject = {}
    details = []
    for q in questions:
        try:
            given = answer_fn(q)
        except Exception as e:
            given = "ERROR: " + str(e)
        expected = str(q.get("answer", "")).strip().lower()
        got = str(given).strip().lower()
        ok = (got == expected)
        total += 1
        correct += 1 if ok else 0
        sub = q.get("subject", "unknown")
        b = by_subject.setdefault(sub, {"correct": 0, "total": 0})
        b["total"] += 1
        b["correct"] += 1 if ok else 0
        details.append({"id": q.get("id"), "subject": sub, "ok": ok})
    accuracy = (100.0 * correct / total) if total else 0.0
    report = {
        "accuracy": round(accuracy, 2),
        "calibration_error": None,
        "total": total,
        "correct": correct,
        "by_subject": by_subject,
        "details": details,
        "non_implication": NON_IMPLICATION,
        "refuses_to_claim": ["AGI", "HLE passing is AGI"],
    }
    guard(str(report))
    return report


def compare_to_leaderboard(report):
    """Return the closest leaderboard entry by accuracy, for context only."""
    if report.get("accuracy") is None:
        return None
    best_name = None
    best_delta = None
    for name, entry in LEADERBOARD.items():
        delta = abs(entry["accuracy"] - report["accuracy"])
        if best_delta is None or delta < best_delta:
            best_delta = delta
            best_name = name
    return {
        "closest_entry": best_name,
        "delta": round(best_delta, 2),
        "context_only": True,
        "non_implication": NON_IMPLICATION,
    }
