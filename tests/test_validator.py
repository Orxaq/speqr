"""Tests for Speqr spec validator."""

from speqr.parser import parse
from speqr.validator import ValidationError, detect_cycles, validate

_ = ValidationError  # imported for public-API surface verification

VALID_DIVIDE = """\
spec Divide
  input numerator: Real
  input denominator: Real
  output result: Real
  precondition denominator != 0
  postcondition result * denominator == numerator
end
"""


def test_valid_spec_passes() -> None:
    spec = parse(VALID_DIVIDE)
    result = validate(spec, registry={})
    assert result.is_valid


def test_precondition_references_undeclared_variable() -> None:
    src = """\
spec Bad
  input x: Real
  output y: Real
  precondition z != 0
end
"""
    spec = parse(src)
    result = validate(spec, registry={})
    assert not result.is_valid
    assert "z" in result.errors[0]


def test_postcondition_references_undeclared_variable() -> None:
    src = """\
spec Bad
  input x: Real
  output y: Real
  postcondition z == x
end
"""
    spec = parse(src)
    result = validate(spec, registry={})
    assert not result.is_valid


def test_spec_reference_resolved() -> None:
    registry = {"is_sorted": object()}  # any truthy value
    src = """\
spec Sort
  input list: List[Int]
  output sorted: List[Int]
  references is_sorted
end
"""
    spec = parse(src)
    result = validate(spec, registry=registry)
    assert result.is_valid


def test_spec_reference_unresolved() -> None:
    src = """\
spec Sort
  input list: List[Int]
  output sorted: List[Int]
  references is_sorted
end
"""
    spec = parse(src)
    result = validate(spec, registry={})  # empty registry
    assert not result.is_valid
    assert "is_sorted" in result.errors[0]


def test_cycle_detection() -> None:
    # A → B → A is a cycle
    graph = {"A": ["B"], "B": ["A"]}
    cycles = detect_cycles(graph)
    assert len(cycles) > 0


def test_no_cycle() -> None:
    graph = {"A": ["B"], "B": ["C"], "C": []}
    assert detect_cycles(graph) == []
