"""Heal: self-healing supervisor that detects its own failure and restarts."""
__version__ = "0.1.0"
from .supervisor import Supervisor, Process, ProcessState
