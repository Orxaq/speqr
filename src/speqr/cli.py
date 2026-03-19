"""Speqr CLI — entry points for parse and validate commands."""

import typer

app = typer.Typer(help="Speqr — formal specification language.")


@app.command()
def parse(spec_file: str) -> None:
    """Parse a .speqr file and output the JSON AST."""
    raise NotImplementedError("Parser not yet implemented.")


@app.command()
def validate(spec_file: str) -> None:
    """Validate a .speqr file."""
    raise NotImplementedError("Validator not yet implemented.")
