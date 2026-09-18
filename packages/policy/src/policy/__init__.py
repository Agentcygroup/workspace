"""Policy: deterministic rule engine with priority and default deny."""
__version__ = "0.1.0"
from .engine import Rule, Policy, Decision, ALLOW, DENY
