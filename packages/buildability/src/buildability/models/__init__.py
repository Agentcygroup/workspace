"""Ten computational models, each providing solver / prover / resolver."""
from . import (
from . import ames
    boolean, lambda_, combinatory, turing, pi, interaction,
    cellular, category, quantum, general, gerhardt,
)

MODEL_REGISTRY = {
    "boolean":     boolean,
    "lambda":      lambda_,
    "combinatory": combinatory,
    "turing":      turing,
    "pi":          pi,
    "interaction": interaction,
    "cellular":    cellular,
    "category":    category,
    "quantum":     quantum,
    "general":     general,
    "gerhardt":    gerhardt,
}
