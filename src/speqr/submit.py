"""HTTP submission to a certification endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx

from speqr.speq import Speq
from speqr.validator import validate


class SpeqrSubmitError(Exception):
    """Raised when submission to the certification endpoint fails."""


@dataclass(frozen=True)
class SubmitResult:
    """Response from the certification endpoint."""

    passed: bool
    findings: list[dict[str, Any]] = field(default_factory=list)


def submit(
    speq: Speq,
    *,
    endpoint: str,
    timeout: float = 30.0,
    headers: dict[str, str] | None = None,
) -> SubmitResult:
    """Submit a speq to a certification endpoint."""
    if not endpoint or not endpoint.strip():
        raise ValueError("endpoint URL is required")
    if not endpoint.strip().startswith(("http://", "https://")):
        raise ValueError("endpoint must be an http:// or https:// URL")

    local_result = validate(speq)
    if not local_result.passed:
        raise ValueError(
            f"speq failed local validation: {'; '.join(local_result.errors)}"
        )

    payload = speq.to_dict()

    try:
        response = httpx.post(
            endpoint,
            json=payload,
            timeout=timeout,
            headers=headers or {},
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, OSError, ValueError) as e:
        raise SpeqrSubmitError(f"submission failed: {e}") from e

    return SubmitResult(
        passed=data.get("passed", False),
        findings=data.get("findings", []),
    )
