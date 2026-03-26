"""Syntax validation for speqr contracts and speqs."""

from __future__ import annotations

from dataclasses import dataclass, field

from speqr.speq import Speq
from speqr.types import CaseRole


@dataclass(frozen=True)
class ValidationResult:
    """Result of syntax validation."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    @property
    def ready_for_certification(self) -> bool:
        return self.passed


def validate(speq: Speq) -> ValidationResult:
    """Validate a speq for syntactic correctness and certification readiness."""
    errors: list[str] = []
    warnings: list[str] = []

    if not speq.contracts:
        warnings.append("speq has no contracts")

    if not speq.version:
        warnings.append("speq has no version")

    targets: dict[str, list[str]] = {}
    for c in speq.contracts:
        targets.setdefault(c.target, []).append(c.name)
    for target, names in targets.items():
        if len(names) > 1:
            warnings.append(
                f"multiple contracts target {target!r}: {', '.join(names)}"
            )

    for c in speq.contracts:
        prefix = f"contract {c.name!r}"
        for role, value in c.roles.items():
            if not value or not value.strip():
                errors.append(f"{prefix}: role {role.name} has empty value")
        if not c.target or not c.target.strip():
            errors.append(f"{prefix}: target is empty")
        cond = c.conditions
        if not cond.preconditions and not cond.postconditions:
            errors.append(f"{prefix}: no preconditions or postconditions")

    return ValidationResult(errors=errors, warnings=warnings)
