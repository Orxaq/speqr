"""OPC Contract model and inline decorator."""

from __future__ import annotations

import functools
from typing import Any

import yaml
from pydantic import BaseModel, model_validator

from speqr.types import CaseRole, GuaranteeLevel, HoareCondition

_ALL_ROLES = set(CaseRole)


class OPCContract(BaseModel):
    """An OPC contract: roles, conditions, and metadata for a unit of code."""

    name: str
    target: str
    roles: dict[CaseRole, str]
    conditions: HoareCondition
    guarantee_target: GuaranteeLevel = GuaranteeLevel.TESTED
    version: str = "1"
    tags: list[str] = []

    @model_validator(mode="after")
    def _validate_completeness(self) -> OPCContract:
        missing = _ALL_ROLES - set(self.roles)
        if missing:
            names = ", ".join(sorted(r.name for r in missing))
            raise ValueError(f"missing role assignments: {names}")
        cond = self.conditions
        if not cond.preconditions and not cond.postconditions:
            raise ValueError(
                "contract must have at least one precondition or postcondition"
            )
        return self

    def to_dict(self) -> dict[str, Any]:
        """Serialize the contract to a plain dictionary."""
        d = self.model_dump()
        d["roles"] = {r.value: v for r, v in self.roles.items()}
        d["guarantee_target"] = self.guarantee_target.label
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> OPCContract:
        """Deserialize a contract from a plain dictionary."""
        roles = {CaseRole(k): v for k, v in d["roles"].items()}
        gt = d.get("guarantee_target", "tested")
        guarantee = next(g for g in GuaranteeLevel if g.label == gt)
        return cls(
            name=d["name"],
            target=d["target"],
            roles=roles,
            conditions=HoareCondition(**d["conditions"]),
            guarantee_target=guarantee,
            version=d.get("version", "1"),
            tags=d.get("tags", []),
        )

    def to_yaml(self) -> str:
        """Serialize the contract to a YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> OPCContract:
        """Deserialize a contract from a YAML string."""
        return cls.from_dict(yaml.safe_load(yaml_str))


def contract(
    *,
    name: str | None = None,
    pre: str | list[str] = "",
    post: str | list[str] = "",
    invariants: str | list[str] = "",
    agent: str,
    patient: str,
    instrument: str,
    result: str,
    source: str,
    destination: str,
    experiencer: str,
    guarantee_target: GuaranteeLevel = GuaranteeLevel.TESTED,
):
    """Inline decorator that attaches an OPC contract to a function."""

    def _wrap(s: str | list[str]) -> list[str]:
        if isinstance(s, str):
            return [s] if s else []
        return s

    def decorator(fn):
        contract_name = name or fn.__name__
        module = fn.__module__ or ""
        qualname = fn.__qualname__ or fn.__name__
        target = f"{module}.{qualname}" if module else qualname

        opc = OPCContract(
            name=contract_name,
            target=target,
            roles={
                CaseRole.AGENT: agent,
                CaseRole.PATIENT: patient,
                CaseRole.INSTRUMENT: instrument,
                CaseRole.RESULT: result,
                CaseRole.SOURCE: source,
                CaseRole.DESTINATION: destination,
                CaseRole.EXPERIENCER: experiencer,
            },
            conditions=HoareCondition(
                preconditions=_wrap(pre),
                postconditions=_wrap(post),
                invariants=_wrap(invariants),
            ),
            guarantee_target=guarantee_target,
        )

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        wrapper.__speqr_contract__ = opc
        return wrapper

    return decorator
