"""ISA VM: executes the opcodes from the ontology stub list that have real semantics."""
__version__ = "0.1.0"
from .machine import Machine, VMError, HALTED
