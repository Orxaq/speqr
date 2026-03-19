"""Serialize SpecNode ↔ JSON. The JSON AST is the contract with Xeqer."""

from __future__ import annotations

import json

from speqr.ast_nodes import (
    CausalAssertionNode,
    InputNode,
    OutputNode,
    PostconditionNode,
    PreconditionNode,
    SpecNode,
    SpecRefNode,
)
from speqr.types import VariableType, sumo_concept_for


def to_json(spec: SpecNode, indent: int = 2) -> str:
    """Serialise SpecNode to JSON string."""
    return json.dumps(_spec_to_dict(spec), indent=indent)


def from_json(text: str) -> SpecNode:
    """Deserialise SpecNode from JSON string."""
    return _dict_to_spec(json.loads(text))


def _spec_to_dict(spec: SpecNode) -> dict[str, object]:
    return {
        "name": spec.name,
        "inputs": [
            {
                "name": n.name,
                "vtype": n.vtype.value,
                "sumo": sumo_concept_for(n.vtype),
            }
            for n in spec.inputs
        ],
        "outputs": [
            {
                "name": n.name,
                "vtype": n.vtype.value,
                "sumo": sumo_concept_for(n.vtype),
            }
            for n in spec.outputs
        ],
        "preconditions": [{"expression": p.expression} for p in spec.preconditions],
        "postconditions": [{"expression": p.expression} for p in spec.postconditions],
        "causal_assertions": [
            {
                "if_var": ca.if_var,
                "direction": ca.direction,
                "by": ca.by,
                "then_var": ca.then_var,
                "then_direction": ca.then_direction,
                "then_by": ca.then_by,
            }
            for ca in spec.causal_assertions
        ],
        "references": [{"name": r.name} for r in spec.references],
    }


def _dict_to_spec(d: dict[str, object]) -> SpecNode:
    inputs_raw = d.get("inputs", [])
    outputs_raw = d.get("outputs", [])
    pres_raw = d.get("preconditions", [])
    posts_raw = d.get("postconditions", [])
    causals_raw = d.get("causal_assertions", [])
    refs_raw = d.get("references", [])

    return SpecNode(
        name=str(d["name"]),
        inputs=[
            InputNode(str(n["name"]), VariableType(n["vtype"]))  # type: ignore[index]
            for n in inputs_raw  # type: ignore[union-attr]
        ],
        outputs=[
            OutputNode(str(n["name"]), VariableType(n["vtype"]))  # type: ignore[index]
            for n in outputs_raw  # type: ignore[union-attr]
        ],
        preconditions=[
            PreconditionNode(str(p["expression"]))  # type: ignore[index]
            for p in pres_raw  # type: ignore[union-attr]
        ],
        postconditions=[
            PostconditionNode(str(p["expression"]))  # type: ignore[index]
            for p in posts_raw  # type: ignore[union-attr]
        ],
        causal_assertions=[
            CausalAssertionNode(
                if_var=str(ca["if_var"]),  # type: ignore[index]
                direction=str(ca["direction"]),  # type: ignore[index]
                by=float(str(ca["by"])),  # type: ignore[index]
                then_var=str(ca["then_var"]),  # type: ignore[index]
                then_direction=str(ca["then_direction"]),  # type: ignore[index]
                then_by=float(str(ca["then_by"])),  # type: ignore[index]
            )
            for ca in causals_raw  # type: ignore[union-attr]
        ],
        references=[
            SpecRefNode(str(r["name"]))  # type: ignore[index]
            for r in refs_raw  # type: ignore[union-attr]
        ],
    )
