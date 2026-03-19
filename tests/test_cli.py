"""Tests for the Speqr CLI."""

import json
from pathlib import Path

from typer.testing import CliRunner

from speqr.cli import app

runner = CliRunner()

DIVIDE_SPEC = """\
spec Divide
  input numerator: Real
  input denominator: Real
  output result: Real
  precondition denominator != 0
  postcondition result * denominator == numerator
end
"""


def test_parse_outputs_json(tmp_path: Path) -> None:
    f = tmp_path / "divide.speqr"
    f.write_text(DIVIDE_SPEC)
    result = runner.invoke(app, ["parse", str(f)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["name"] == "Divide"


def test_validate_valid_spec(tmp_path: Path) -> None:
    f = tmp_path / "divide.speqr"
    f.write_text(DIVIDE_SPEC)
    result = runner.invoke(app, ["validate", str(f)])
    assert result.exit_code == 0
    assert "valid" in result.output.lower()


def test_validate_invalid_spec(tmp_path: Path) -> None:
    bad = """\
spec Bad
  input x: Real
  output y: Real
  precondition z != 0
end
"""
    f = tmp_path / "bad.speqr"
    f.write_text(bad)
    result = runner.invoke(app, ["validate", str(f)])
    assert result.exit_code == 1
    assert "z" in result.output


def test_parse_missing_file() -> None:
    result = runner.invoke(app, ["parse", "nonexistent.speqr"])
    assert result.exit_code != 0


def test_cli_smoke_end_to_end(tmp_path: Path) -> None:
    f = tmp_path / "divide.speqr"
    f.write_text(DIVIDE_SPEC)
    result = runner.invoke(app, ["validate", str(f)])
    assert result.exit_code == 0
    result2 = runner.invoke(app, ["parse", str(f)])
    assert result2.exit_code == 0
    data = json.loads(result2.output)
    assert data["name"] == "Divide"
