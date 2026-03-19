"""Tests for Speqr AST ↔ JSON serializer."""

import json

from speqr.ast_nodes import SpecNode
from speqr.parser import parse
from speqr.serializer import from_json, to_json

DIVIDE_SPEC = """\
spec Divide
  input numerator: Real
  input denominator: Real
  output result: Real
  precondition denominator != 0
  postcondition result * denominator == numerator
end
"""


def test_to_json_is_valid_json() -> None:
    spec = parse(DIVIDE_SPEC)
    output = to_json(spec)
    parsed = json.loads(output)
    assert parsed["name"] == "Divide"


def test_to_json_contains_inputs() -> None:
    spec = parse(DIVIDE_SPEC)
    data = json.loads(to_json(spec))
    assert len(data["inputs"]) == 2
    assert data["inputs"][0]["name"] == "numerator"
    assert data["inputs"][0]["vtype"] == "Real"
    assert data["inputs"][0]["sumo"] == "RealNumber"


def test_roundtrip() -> None:
    spec = parse(DIVIDE_SPEC)
    restored = from_json(to_json(spec))
    assert isinstance(restored, SpecNode)
    assert restored.name == spec.name
    assert len(restored.inputs) == len(spec.inputs)
    assert restored.preconditions[0].expression == spec.preconditions[0].expression
