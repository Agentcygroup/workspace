import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))
from buildability.models import MODEL_REGISTRY


def test_ames_registered():
    assert "ames" in MODEL_REGISTRY


def test_ames_prover_rejects_non_ames():
    m = MODEL_REGISTRY["ames"]
    assert m.prover({"model": "other"}, None) is False
