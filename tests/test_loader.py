"""Tests for YAML separate-doc loading."""

import pytest
from pathlib import Path
from speqr.loader import load_speq_file, load_speq_string
from speqr.types import CaseRole


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

MINIMAL_YAML = """
name: minimal
contracts:
  - name: check
    target: mod.check
    pre: "x > 0"
    post: "result is bool"
    roles:
      agent: checker
      patient: input
      instrument: logic
      result: output
      source: data
      destination: store
      experiencer: user
"""


class TestLoadSpeqString:
    def test_non_dict_yaml_raises(self):
        with pytest.raises(ValueError, match="mapping"):
            load_speq_string("- item1\n- item2")

    def test_yaml_parse_error_raises(self):
        # A tab character in a YAML value position causes a parse error
        with pytest.raises(ValueError, match="invalid YAML"):
            load_speq_string("key: [\nunclosed bracket")

    def test_loads_valid_yaml(self):
        speq = load_speq_string(VALID_YAML)
        assert speq.name == "my_system"
        assert len(speq.contracts) == 1
        assert speq.contracts[0].name == "transform"

    def test_roles_are_case_roles(self):
        speq = load_speq_string(VALID_YAML)
        contract = speq.contracts[0]
        assert CaseRole.AGENT in contract.roles

    def test_minimal_yaml(self):
        speq = load_speq_string(MINIMAL_YAML)
        assert speq.name == "minimal"
        assert speq.version == "0.1.0"


class TestLoadSpeqFile:
    def test_loads_from_path(self, tmp_path: Path):
        f = tmp_path / "test.speq.yaml"
        f.write_text(VALID_YAML)
        speq = load_speq_file(f)
        assert speq.name == "my_system"

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_speq_file(tmp_path / "nope.yaml")

    def test_invalid_yaml_raises(self, tmp_path: Path):
        f = tmp_path / "bad.yaml"
        f.write_text(":::not yaml:::")
        with pytest.raises(ValueError):
            load_speq_file(f)

    def test_missing_name_raises(self, tmp_path: Path):
        f = tmp_path / "bad.yaml"
        f.write_text("contracts: []")
        with pytest.raises(ValueError, match="name"):
            load_speq_file(f)
