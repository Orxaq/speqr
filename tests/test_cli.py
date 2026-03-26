"""Tests for speqr CLI."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from speqr.cli import main
from speqr.submit import SubmitResult, SpeqrSubmitError


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

    def test_validate_with_warnings(self, tmp_path):
        # Two contracts targeting the same function triggers a duplicate-target warning
        dup_target_yaml = """
name: dup_target_system
version: "1.0.0"
contracts:
  - name: transform_a
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
  - name: transform_b
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
        f = tmp_path / "warn.speq.yaml"
        f.write_text(dup_target_yaml)
        runner = CliRunner()
        result = runner.invoke(main, ["validate", str(f)])
        assert result.exit_code == 0
        assert "warning" in result.output.lower()


class TestSubmitCommand:
    def test_missing_endpoint_errors(self, tmp_path):
        f = tmp_path / "test.speq.yaml"
        f.write_text(VALID_YAML)
        runner = CliRunner()
        result = runner.invoke(main, ["submit", str(f)])
        assert result.exit_code == 1
        assert "endpoint" in result.output.lower()

    def test_submit_success(self, tmp_path):
        f = tmp_path / "test.speq.yaml"
        f.write_text(VALID_YAML)
        runner = CliRunner()
        mock_result = SubmitResult(passed=True, findings=[])
        with patch("speqr.cli.submit_speq", return_value=mock_result):
            result = runner.invoke(
                main, ["submit", str(f), "--endpoint", "https://verify.example.com/certify"]
            )
        assert result.exit_code == 0
        assert "CERTIFIED" in result.output

    def test_submit_rejected(self, tmp_path):
        f = tmp_path / "test.speq.yaml"
        f.write_text(VALID_YAML)
        runner = CliRunner()
        mock_result = SubmitResult(
            passed=False,
            findings=[{"rule": "C-010", "message": "role incomplete"}],
        )
        with patch("speqr.cli.submit_speq", return_value=mock_result):
            result = runner.invoke(
                main, ["submit", str(f), "--endpoint", "https://verify.example.com/certify"]
            )
        assert result.exit_code == 1
        assert "REJECTED" in result.output
        assert "C-010" in result.output
        assert "role incomplete" in result.output

    def test_submit_connection_error(self, tmp_path):
        f = tmp_path / "test.speq.yaml"
        f.write_text(VALID_YAML)
        runner = CliRunner()
        with patch("speqr.cli.submit_speq", side_effect=SpeqrSubmitError("connection refused")):
            result = runner.invoke(
                main, ["submit", str(f), "--endpoint", "https://verify.example.com/certify"]
            )
        assert result.exit_code == 1
        assert "error" in result.output.lower()

    def test_submit_invalid_file(self, tmp_path):
        f = tmp_path / "bad.speq.yaml"
        f.write_text("- item1\n- item2")
        runner = CliRunner()
        result = runner.invoke(
            main, ["submit", str(f), "--endpoint", "https://verify.example.com/certify"]
        )
        assert result.exit_code == 1
        assert "error" in result.output.lower()
