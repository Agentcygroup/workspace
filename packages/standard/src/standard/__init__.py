"""Execution Standard v1.0.0 enforcement."""
__version__ = "0.1.0"
STANDARD_VERSION = "1.0.0"
from .articles import ARTICLES, get_article
from .gaps import MOATS, IMPLEMENTED_MOATS, GAP_MOATS
from .refusals import REFUSALS, refuses
from .conformance import conformance_report
