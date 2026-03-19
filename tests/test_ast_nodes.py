"""Tests for Speqr AST node dataclasses."""

from speqr.ast_nodes import (
    CausalAssertionNode,
    InputNode,
    OutputNode,
    PostconditionNode,
    PreconditionNode,
    SpecNode,
    SpecRefNode,
)
from speqr.types import VariableType


def test_input_node() -> None:
    node = InputNode(name="numerator", vtype=VariableType.REAL)
    assert node.name == "numerator"
    assert node.vtype == VariableType.REAL


def test_output_node() -> None:
    node = OutputNode(name="result", vtype=VariableType.REAL)
    assert node.name == "result"


def test_precondition_node() -> None:
    node = PreconditionNode(expression="denominator != 0")
    assert node.expression == "denominator != 0"


def test_postcondition_node() -> None:
    node = PostconditionNode(expression="result * denominator == numerator")
    assert "denominator" in node.expression


def test_causal_assertion_node() -> None:
    node = CausalAssertionNode(
        if_var="celsius",
        direction="increases",
        by=1,
        then_var="fahrenheit",
        then_direction="increases",
        then_by=1.8,
    )
    assert node.if_var == "celsius"
    assert node.then_by == 1.8


def test_spec_ref_node() -> None:
    node = SpecRefNode(name="is_sorted")
    assert node.name == "is_sorted"


def test_spec_node_full() -> None:
    spec = SpecNode(
        name="Divide",
        inputs=[
            InputNode("numerator", VariableType.REAL),
            InputNode("denominator", VariableType.REAL),
        ],
        outputs=[OutputNode("result", VariableType.REAL)],
        preconditions=[PreconditionNode("denominator != 0")],
        postconditions=[PostconditionNode("result * denominator == numerator")],
        causal_assertions=[],
        references=[],
    )
    assert spec.name == "Divide"
    assert len(spec.inputs) == 2
    assert len(spec.preconditions) == 1


def test_spec_node_references() -> None:
    spec = SpecNode(
        name="Sort",
        inputs=[],
        outputs=[],
        preconditions=[],
        postconditions=[],
        causal_assertions=[],
        references=[SpecRefNode("is_sorted")],
    )
    assert spec.references[0].name == "is_sorted"
