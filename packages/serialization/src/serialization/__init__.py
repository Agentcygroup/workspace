"""Serialization: canonical JSON with schema validation."""
__version__ = "0.1.0"
from .canon import canonical, parse
from .schema import Schema, SchemaError
