"""Ledger: append-only hash-chained record with claim/evidence/link primitives."""
__version__ = "0.1.0"
from .chain import Chain, ChainError
from .claims import Claim, Evidence, Link, validate_link
