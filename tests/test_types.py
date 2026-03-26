"""Tests for speqr core types."""

import pytest
from speqr.types import CaseRole, GuaranteeLevel, HoareCondition


class TestCaseRole:
    def test_has_seven_roles(self):
        assert len(CaseRole) == 7

    def test_role_names(self):
        expected = {"AGENT", "PATIENT", "INSTRUMENT", "RESULT", "SOURCE", "DESTINATION", "EXPERIENCER"}
        assert {r.name for r in CaseRole} == expected

    def test_role_values_are_lowercase(self):
        for role in CaseRole:
            assert role.value == role.name.lower()


class TestGuaranteeLevel:
    def test_has_four_levels(self):
        assert len(GuaranteeLevel) == 4

    def test_ordering(self):
        assert GuaranteeLevel.PROVEN.rank > GuaranteeLevel.VERIFIED.rank
        assert GuaranteeLevel.VERIFIED.rank > GuaranteeLevel.BOUNDED.rank
        assert GuaranteeLevel.BOUNDED.rank > GuaranteeLevel.TESTED.rank

    def test_comparison(self):
        assert GuaranteeLevel.PROVEN > GuaranteeLevel.TESTED
        assert GuaranteeLevel.TESTED < GuaranteeLevel.VERIFIED


class TestHoareCondition:
    def test_string_conditions(self):
        hc = HoareCondition(
            preconditions=["x > 0"],
            postconditions=["result >= 0"],
            invariants=["x is unchanged"],
        )
        assert len(hc.preconditions) == 1
        assert len(hc.postconditions) == 1
        assert len(hc.invariants) == 1

    def test_callable_conditions(self):
        pre = lambda ctx: ctx.get("x", 0) > 0
        hc = HoareCondition(
            preconditions=[pre],
            postconditions=["result >= 0"],
        )
        assert callable(hc.preconditions[0])

    def test_empty_invariants_default(self):
        hc = HoareCondition(
            preconditions=["x > 0"],
            postconditions=["result >= 0"],
        )
        assert hc.invariants == []

    def test_serialization_round_trip(self):
        hc = HoareCondition(
            preconditions=["x > 0"],
            postconditions=["result >= 0"],
            invariants=["x is unchanged"],
        )
        d = hc.model_dump()
        restored = HoareCondition.model_validate(d)
        assert restored.preconditions == hc.preconditions
