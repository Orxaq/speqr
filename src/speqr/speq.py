"""Speq — a collection of OPC contracts describing a system."""

from __future__ import annotations

import inspect
from types import ModuleType
from typing import Any

from pydantic import BaseModel

from speqr.contract import OPCContract


class Speq(BaseModel):
    """A named, versioned collection of OPC contracts."""

    name: str
    version: str = "0.1.0"
    contracts: list[OPCContract] = []

    def add(self, contract: OPCContract) -> Speq:
        existing = {c.name for c in self.contracts}
        if contract.name in existing:
            raise ValueError(f"duplicate contract name: {contract.name!r}")
        return self.model_copy(update={"contracts": [*self.contracts, contract]})

    def get(self, name: str) -> OPCContract | None:
        for c in self.contracts:
            if c.name == name:
                return c
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "contracts": [c.to_dict() for c in self.contracts],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Speq:
        contracts = [OPCContract.from_dict(c) for c in d.get("contracts", [])]
        return cls(name=d["name"], version=d.get("version", "0.1.0"), contracts=contracts)

    @classmethod
    def collect(cls, name: str, module: ModuleType) -> Speq:
        """Collect all @contract-decorated functions from a module."""
        contracts: list[OPCContract] = []
        for _name, obj in inspect.getmembers(module):
            if hasattr(obj, "__speqr_contract__"):
                contracts.append(obj.__speqr_contract__)
        return cls(name=name, contracts=contracts)
