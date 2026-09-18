"""Policy Platform: multi-tenant rule evaluation with drift detection and audit."""
__version__ = "0.1.0"
from .platform import Platform, Tenant, AuditEntry
from .drift import detect_drift
