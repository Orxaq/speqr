"""Speqr — Define, validate, and certify OPC contracts for your code."""

__version__ = "0.1.0"

from speqr.types import CaseRole, GuaranteeLevel, HoareCondition
from speqr.contract import OPCContract, contract
from speqr.speq import Speq
from speqr.validator import validate, ValidationResult
from speqr.loader import load_speq_file, load_speq_string
from speqr.submit import submit, SubmitResult, SpeqrSubmitError

__all__ = [
    "CaseRole",
    "GuaranteeLevel",
    "HoareCondition",
    "OPCContract",
    "Speq",
    "contract",
    "validate",
    "ValidationResult",
    "load_speq_file",
    "load_speq_string",
    "submit",
    "SubmitResult",
    "SpeqrSubmitError",
]
