"""Grammar smoke tests — full parser integration in Task 1.5."""

from pathlib import Path

from lark import Lark

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
