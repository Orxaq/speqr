"""AST node dataclasses for Speqr specifications."""

from __future__ import annotations

from dataclasses import dataclass, field

from speqr.types import VariableType


@dataclass
class InputNode:
    name: str
    vtype: VariableType


@dataclass
class OutputNode:
    name: str
    vtype: VariableType


@dataclass
class PreconditionNode:
    expression: str


@dataclass
class PostconditionNode:
    expression: str


@dataclass
class CausalAssertionNode:
    if_var: str
    direction: str  # "increases" | "decreases"
    by: float
    then_var: str
    then_direction: str
    then_by: float


@dataclass
class SpecRefNode:
    """A reference to another named spec (composability)."""

    name: str


@dataclass
class SpecNode:
    name: str
    inputs: list[InputNode]
    outputs: list[OutputNode]
    preconditions: list[PreconditionNode]
    postconditions: list[PostconditionNode]
    causal_assertions: list[CausalAssertionNode]
    references: list[SpecRefNode] = field(default_factory=list)
