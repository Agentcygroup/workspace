import json
from pathlib import Path
from . import (
    LEADERBOARD, NON_IMPLICATION,
    claim_hle_passing_is_real,
    claim_hle_passing_is_not_agi,
    claim_agi_has_no_benchmark,
)


def build_all(dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    p = dest / "leaderboard.json"
    p.write_text(json.dumps(LEADERBOARD, indent=2))
    written.append(str(p))
    p = dest / "claim_1_real.json"
    p.write_text(json.dumps(claim_hle_passing_is_real(), indent=2))
    written.append(str(p))
    p = dest / "claim_2_not_agi.json"
    p.write_text(json.dumps(claim_hle_passing_is_not_agi(), indent=2))
    written.append(str(p))
    p = dest / "claim_3_no_agi_benchmark.json"
    p.write_text(json.dumps(claim_agi_has_no_benchmark(), indent=2))
    written.append(str(p))
    p = dest / "non_implication.json"
    p.write_text(json.dumps({"non_implication": NON_IMPLICATION}, indent=2))
    written.append(str(p))
    return written
