"""Kernel: operators, axioms, mappings, envelope, sandbox. MP1-MP6 enforced."""
__version__ = "0.1.0"
from .envelope import Envelope, make_envelope, verify_envelope
from .operators import OPERATORS, apply_operator, denotation
from .axioms import AXIOMS, check_axiom, independence_report
from .mappings import MAPPINGS, map_envelope, preservation_report
from .sandbox import run_in_sandbox, SandboxRejection
