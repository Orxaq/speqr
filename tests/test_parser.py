"""Grammar smoke tests — full parser integration in Task 1.5."""

from pathlib import Path

from lark import Lark

from speqr.ast_nodes import SpecNode
from speqr.parser import parse
from speqr.types import VariableType

GRAMMAR = (Path(__file__).parent.parent / "src" / "speqr" / "grammar.lark").read_text()

DIVIDE_SPEC = """\
spec Divide
  input numerator: Real
  input denominator: Real
  output result: Real
  precondition denominator != 0
  postcondition result * denominator == numerator
end
"""


def test_grammar_loads() -> None:
    parser = Lark(GRAMMAR, parser="earley", propagate_positions=False)
    assert parser is not None


def test_grammar_parses_divide() -> None:
    parser = Lark(GRAMMAR, parser="earley")
    tree = parser.parse(DIVIDE_SPEC)
    assert tree.data == "start"
    assert len(tree.children) == 1  # one spec


def test_grammar_parses_causal_assertion() -> None:
    src = """\
spec TempConvert
  input celsius: Real
  output fahrenheit: Real
  causal assertion
    if celsius increases by 1
    then fahrenheit increases by 1.8
end
"""
    parser = Lark(GRAMMAR, parser="earley")
    tree = parser.parse(src)
    assert tree is not None


def test_grammar_handles_crlf() -> None:
    src = DIVIDE_SPEC.replace("\n", "\r\n")
    parser = Lark(GRAMMAR, parser="earley")
    tree = parser.parse(src)
    assert tree is not None


def test_parse_returns_spec_node() -> None:
    spec = parse(DIVIDE_SPEC)
    assert isinstance(spec, SpecNode)
    assert spec.name == "Divide"


def test_parse_inputs() -> None:
    spec = parse(DIVIDE_SPEC)
    assert len(spec.inputs) == 2
    assert spec.inputs[0].name == "numerator"
    assert spec.inputs[0].vtype == VariableType.REAL


def test_parse_precondition() -> None:
    spec = parse(DIVIDE_SPEC)
    assert len(spec.preconditions) == 1
    assert "denominator" in spec.preconditions[0].expression


def test_parse_postcondition() -> None:
    spec = parse(DIVIDE_SPEC)
    assert len(spec.postconditions) == 1


def test_parse_causal_assertion() -> None:
    src = """\
spec TempConvert
  input celsius: Real
  output fahrenheit: Real
  causal assertion
    if celsius increases by 1
    then fahrenheit increases by 1.8
end
"""
    spec = parse(src)
    assert len(spec.causal_assertions) == 1
    ca = spec.causal_assertions[0]
    assert ca.if_var == "celsius"
    assert ca.then_by == 1.8


def test_parse_spec_reference() -> None:
    src = """\
spec Sort
  input list: List[Int]
  output sorted: List[Int]
  references is_sorted
end
"""
    spec = parse(src)
    assert len(spec.references) == 1
    assert spec.references[0].name == "is_sorted"
