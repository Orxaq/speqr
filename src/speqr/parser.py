"""Parse Speqr source text into an AST."""

from __future__ import annotations

from pathlib import Path

from lark import Lark, Token, Transformer

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

_GRAMMAR = (Path(__file__).parent / "grammar.lark").read_text()
_PARSER = Lark(_GRAMMAR, parser="earley", propagate_positions=False)


class _SpecTransformer(Transformer):
    # ------------------------------------------------------------------ types
    def int_type(self, _: list[object]) -> VariableType:
        return VariableType.INT

    def real_type(self, _: list[object]) -> VariableType:
        return VariableType.REAL

    def bool_type(self, _: list[object]) -> VariableType:
        return VariableType.BOOL

    def string_type(self, _: list[object]) -> VariableType:
        return VariableType.STRING

    def list_type(self, _: list[object]) -> VariableType:
        return VariableType.LIST

    def set_type(self, _: list[object]) -> VariableType:
        return VariableType.SET

    def map_type(self, _: list[object]) -> VariableType:
        return VariableType.MAP

    # --------------------------------------------------------------- direction
    def direction(self, children: list[object]) -> str:
        # children[0] is an INCREASES or DECREASES token
        return str(children[0])

    # -------------------------------------------------------------- expression
    def expression(self, children: list[object]) -> str:
        return str(children[0]).strip()

    # ------------------------------------------------------------ declarations
    def input_decl(self, children: list[object]) -> InputNode:
        # children: [NAME, vtype, NEWLINE]
        name = str(children[0])
        vtype: VariableType = children[1]  # type: ignore[assignment]
        return InputNode(name, vtype)

    def output_decl(self, children: list[object]) -> OutputNode:
        # children: [NAME, vtype, NEWLINE]
        name = str(children[0])
        vtype: VariableType = children[1]  # type: ignore[assignment]
        return OutputNode(name, vtype)

    def precondition(self, children: list[object]) -> PreconditionNode:
        # children: [expression_str, NEWLINE]
        return PreconditionNode(str(children[0]))

    def postcondition(self, children: list[object]) -> PostconditionNode:
        # children: [expression_str, NEWLINE]
        return PostconditionNode(str(children[0]))

    def causal_assertion(self, children: list[object]) -> CausalAssertionNode:
        # After transformation, NEWLINEs are tokens (not filtered).
        # Filter to non-NEWLINE items.
        items = [
            c for c in children if not (isinstance(c, Token) and c.type == "NEWLINE")
        ]
        # items: [if_var, dir, by, then_var, then_dir, then_by]
        if_var = str(items[0])
        direction = str(items[1])
        by = float(str(items[2]))
        then_var = str(items[3])
        then_direction = str(items[4])
        then_by = float(str(items[5]))
        return CausalAssertionNode(
            if_var, direction, by, then_var, then_direction, then_by
        )

    def spec_ref(self, children: list[object]) -> SpecRefNode:
        # children: [NAME, NEWLINE]
        return SpecRefNode(str(children[0]))

    # --------------------------------------------------------------- spec_body
    def spec_body(self, children: list[object]) -> object:
        # Unwrap the single AST node child.
        return children[0]

    # ------------------------------------------------------------------- spec
    def spec(self, children: list[object]) -> SpecNode:
        # children: [NAME, NEWLINE, *spec_body_items...]
        name = str(children[0])
        inputs: list[InputNode] = []
        outputs: list[OutputNode] = []
        pres: list[PreconditionNode] = []
        posts: list[PostconditionNode] = []
        causals: list[CausalAssertionNode] = []
        refs: list[SpecRefNode] = []
        for child in children[1:]:
            if isinstance(child, InputNode):
                inputs.append(child)
            elif isinstance(child, OutputNode):
                outputs.append(child)
            elif isinstance(child, PreconditionNode):
                pres.append(child)
            elif isinstance(child, PostconditionNode):
                posts.append(child)
            elif isinstance(child, CausalAssertionNode):
                causals.append(child)
            elif isinstance(child, SpecRefNode):
                refs.append(child)
        return SpecNode(name, inputs, outputs, pres, posts, causals, refs)

    # ------------------------------------------------------------------ start
    def start(self, children: list[object]) -> list[SpecNode]:
        return [c for c in children if isinstance(c, SpecNode)]


def parse(source: str) -> SpecNode:
    """Parse Speqr source text and return a SpecNode for the first spec."""
    tree = _PARSER.parse(source)
    specs: list[SpecNode] = _SpecTransformer().transform(tree)
    if not specs:
        raise ValueError("No spec found in source")
    return specs[0]
