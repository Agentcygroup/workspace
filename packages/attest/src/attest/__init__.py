"""Attest: in-toto style attestations backed by local hashing."""
__version__ = "0.1.0"
from .statement import Statement, Subject, build_statement
from .sbom import SBOM, generate_sbom
