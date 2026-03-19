"""Speqr — formal specification language for declaring code behaviour."""

__version__ = "0.1.0"

from speqr.parser import parse
from speqr.serializer import from_json, to_json
from speqr.validator import validate

__all__ = ["parse", "validate", "to_json", "from_json", "__version__"]
