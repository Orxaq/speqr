"""Speqr CLI — `speqr parse` and `speqr validate`."""

from __future__ import annotations

from pathlib import Path

import typer

from speqr.parser import parse
from speqr.serializer import to_json
from speqr.validator import validate

app = typer.Typer(help="Speqr — formal specification language CLI")


@app.command(name="parse")
def parse_cmd(
    file: Path = typer.Argument(..., help="Path to .speqr file"),  # noqa: B008
) -> None:
    """Parse a Speqr file and output its JSON AST."""
    if not file.exists():
        typer.echo(f"File not found: {file}", err=True)
        raise typer.Exit(1)
    spec = parse(file.read_text())
    typer.echo(to_json(spec))


@app.command(name="validate")
def validate_cmd(
    file: Path = typer.Argument(..., help="Path to .speqr file"),  # noqa: B008
) -> None:
    """Validate a Speqr file and report errors."""
    if not file.exists():
        typer.echo(f"File not found: {file}", err=True)
        raise typer.Exit(1)
    spec = parse(file.read_text())
    result = validate(spec, registry={})
    if result.is_valid:
        typer.echo("Spec is valid")
    else:
        for err in result.errors:
            typer.echo(f"Error: {err}")
        raise typer.Exit(1)
