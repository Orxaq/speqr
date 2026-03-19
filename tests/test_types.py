"""Tests for VariableType enum and SUMO mappings."""

import pytest

from speqr.types import VariableType, sumo_concept_for


def test_variable_type_members() -> None:
    """All seven primitive types exist."""
    assert VariableType.INT
    assert VariableType.REAL
    assert VariableType.BOOL
    assert VariableType.STRING
    assert VariableType.LIST
    assert VariableType.SET
    assert VariableType.MAP


def test_sumo_mapping_int() -> None:
    assert sumo_concept_for(VariableType.INT) == "Integer"


def test_sumo_mapping_real() -> None:
    assert sumo_concept_for(VariableType.REAL) == "RealNumber"


def test_sumo_mapping_bool() -> None:
    assert sumo_concept_for(VariableType.BOOL) == "TruthValue"


def test_sumo_mapping_string() -> None:
    assert sumo_concept_for(VariableType.STRING) == "SymbolicString"


def test_sumo_mapping_collection_types() -> None:
    assert sumo_concept_for(VariableType.LIST) == "List"
    assert sumo_concept_for(VariableType.SET) == "SpeqrSet"
    assert sumo_concept_for(VariableType.MAP) == "SpeqrMap"


def test_sumo_mapping_unknown_raises() -> None:
    with pytest.raises(KeyError):
        sumo_concept_for("NotAType")  # type: ignore[arg-type]
