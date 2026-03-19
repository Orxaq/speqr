"""Validate a parsed SpecNode against type and reference rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from speqr.ast_nodes import SpecNode


class ValidationError(Exception):
    """Raised when a spec fails validation."""


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)


def _declared_names(spec: SpecNode) -> set[str]:
    return {n.name for n in spec.inputs} | {n.name for n in spec.outputs}


def _names_in_expression(expr: str) -> set[str]:
    """Extract identifiers from an expression string."""
    return {t for t in re.findall(r"\b[a-zA-Z_]\w*\b", expr)}


def validate(spec: SpecNode, registry: dict[str, object]) -> ValidationResult:
    """Validate a SpecNode. registry maps spec names → SpecNode (or any value)."""
    errors: list[str] = []
    declared = _declared_names(spec)

    for pre in spec.preconditions:
        for name in _names_in_expression(pre.expression):
            if name not in declared:
                errors.append(f"Precondition references undeclared variable '{name}'")

    for post in spec.postconditions:
        for name in _names_in_expression(post.expression):
            if name not in declared:
                errors.append(f"Postcondition references undeclared variable '{name}'")

    for ref in spec.references:
        if ref.name not in registry:
            errors.append(f"Unresolved spec reference '{ref.name}'")

    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def detect_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Return list of cycles in a reference graph. [] if acyclic."""
    visited: set[str] = set()
    path: list[str] = []
    cycles: list[list[str]] = []

    def dfs(node: str) -> None:
        if node in path:
            idx = path.index(node)
            cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        path.append(node)
        for neighbour in graph.get(node, []):
            dfs(neighbour)
        path.pop()

    for node in graph:
        dfs(node)
    return cycles
