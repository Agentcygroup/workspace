"""Ontology: 16 levels with kinds, binds, invariants, and implementation status."""
__version__ = "0.1.0"
from .levels import LEVELS, KIND_INDEX, BINDS, INVARIANTS
from .validate import validate, gap_register, implementation_status
