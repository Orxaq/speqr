"""Tests for speqr CLI."""

import pytest
from click.testing import CliRunner
from speqr.cli import main


VALID_YAML = """
name: my_system
version: "1.0.0"
contracts:
  - name: transform
    target: mymodule.transform
    pre: "input is valid"
    post: "output is transformed"
    roles:
      agent: transformer
      patient: data
      instrument: algorithm
      result: output
      source: raw_input
      destination: data_store
      experiencer: operator
"""

INVALID_YAML = """
name: bad_system
contracts:
  - name: bad
    target: mod.bad
    pre: "valid"
    post: "done"
    roles:
      agent: ""
      patient: p
      instrument: i
      result: r
      source: s
      destination: d
      experiencer: e
"""


class TestValidateCommand:
    def test_valid_file(self, tmp_path):
        f = tmp_path / "test.speq.yaml"
        f.write_text(VALID_YAML)
        runner = CliRunner()
        result = runner.invoke(main, ["validate", str(f)])
        assert result.exit_code == 0
        assert "ready for certification" in result.output.lower()

    def test_invalid_file(self, tmp_path):
        f = tmp_path / "test.speq.yaml"
        f.write_text(INVALID_YAML)
        runner = CliRunner()
        result = runner.invoke(main, ["validate", str(f)])
        assert result.exit_code == 1
        assert "error" in result.output.lower()

    def test_missing_file(self):
        runner = CliRunner()
        result = runner.invoke(main, ["validate", "/nonexistent.yaml"])
        assert result.exit_code == 1

    def test_glob_pattern(self, tmp_path):
        f1 = tmp_path / "a.speq.yaml"
        f1.write_text(VALID_YAML)
        f2 = tmp_path / "b.speq.yaml"
        f2.write_text(VALID_YAML)
        runner = CliRunner()
        result = runner.invoke(main, ["validate", str(tmp_path / "*.speq.yaml")])
        assert result.exit_code == 0


class TestSubmitCommand:
    def test_missing_endpoint_errors(self, tmp_path):
        f = tmp_path / "test.speq.yaml"
        f.write_text(VALID_YAML)
        runner = CliRunner()
        result = runner.invoke(main, ["submit", str(f)])
        assert result.exit_code == 1
        assert "endpoint" in result.output.lower()
