"""Core types for speqr OPC contracts."""

from __future__ import annotations

import enum
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, field_validator


class CaseRole(str, enum.Enum):
    """The 7 CASS CaseRoles describing participants in a contract."""

    AGENT = "agent"
    PATIENT = "patient"
    INSTRUMENT = "instrument"
    RESULT = "result"
    SOURCE = "source"
    DESTINATION = "destination"
    EXPERIENCER = "experiencer"


class GuaranteeLevel(enum.Enum):
    """Assurance levels for verified contracts. PROVEN > VERIFIED > BOUNDED > TESTED"""

    PROVEN = ("proven", 4)
    VERIFIED = ("verified", 3)
    BOUNDED = ("bounded", 2)
    TESTED = ("tested", 1)

    def __init__(self, label: str, rank: int) -> None:
        self.label = label
        self._rank = rank

    @property
    def rank(self) -> int:
        return self._rank

    def __gt__(self, other: GuaranteeLevel) -> bool:
        if not isinstance(other, GuaranteeLevel):
            return NotImplemented
        return self._rank > other._rank

    def __lt__(self, other: GuaranteeLevel) -> bool:
        if not isinstance(other, GuaranteeLevel):
            return NotImplemented
        return self._rank < other._rank

    def __ge__(self, other: GuaranteeLevel) -> bool:
        if not isinstance(other, GuaranteeLevel):
            return NotImplemented
        return self._rank >= other._rank

    def __le__(self, other: GuaranteeLevel) -> bool:
        if not isinstance(other, GuaranteeLevel):
            return NotImplemented
        return self._rank <= other._rank


class HoareCondition(BaseModel):
    """Pre/post/invariant conditions for an OPC contract."""

    preconditions: list[str | Callable[..., Any]] = []
    postconditions: list[str | Callable[..., Any]] = []
    invariants: list[str | Callable[..., Any]] = []

    model_config = {"arbitrary_types_allowed": True}
