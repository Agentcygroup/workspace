"""Lexicon: industry terms mapped to primitives with provenance.

Every term carries a source. Sources are limited to what can be cited:
W3C vocabularies, ISO vocabulary standards, NIST glossaries, industry
taxonomies. Terms with no authoritative source are marked emergent.
"""
__version__ = "0.1.0"
from .terms import TERMS, get_term, terms_by_source, terms_by_atom
from .validate import validate_term, validate_all
