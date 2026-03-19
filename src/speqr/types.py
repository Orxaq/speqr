"""VariableType — primitive types for Speqr specifications.

Each type is grounded in SUMO (Suggested Upper Merged Ontology).
SUMO reference: https://www.ontologyportal.org/

Note: List maps to SUMO List; Set and Map are Speqr-defined extensions
(SUMO has SetOrClass but not a generic Map concept).
Full SUMO grounding for collections is deferred to Qennix.
"""
from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

_SUMO_DATA: dict[str, dict[str, str]] = json.loads(
    (Path(__file__).parent / "sumo_types.json").read_text()
)


class VariableType(StrEnum):
    INT = "Int"
    REAL = "Real"
    BOOL = "Bool"
    STRING = "String"
    LIST = "List"
    SET = "Set"
    MAP = "Map"


def sumo_concept_for(vtype: VariableType) -> str:
    """Return the SUMO concept name for a VariableType."""
    if not isinstance(vtype, VariableType):
        raise KeyError(f"Unknown type: {vtype!r}")
    return _SUMO_DATA[vtype.name]["sumo"]
