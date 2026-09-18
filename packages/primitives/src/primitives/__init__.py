"""Compositional primitives.

Six verb categories. Every primitive has the same shape:

    id              str, verb-prefix + noun + ordinal
    verb            one of VERBS
    kind            one of KINDS[verb]
    accepts         list of primitive ids it consumes
    emits           list of primitive ids it produces
    industry_terms  list of lexicon term ids this primitive maps to
    provenance      list of source citations

A system for an industry is a labelled graph over these atoms. This package
provides the atoms. It does not provide the constructor, the industry
requirements parser, or the graph evaluator. Those are separate packages.
"""
__version__ = "0.1.0"
from .verbs import VERBS, KINDS
from .atoms import ATOMS, get_atom, atoms_by_verb, atoms_by_kind
from .validate import validate_atom, validate_all
from .compose import compose
