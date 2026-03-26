"""Tests for speqr syntax validation."""

import pytest
from speqr.validator import validate, ValidationResult
from speqr.contract import OPCContract
from speqr.speq import Speq
from speqr.types import CaseRole, HoareCondition


def _make_contract(name: str = "test", **overrides) -> OPCContract:
    defaults = dict(
        name=name,
        target=f"mod.{name}",
        roles={r: r.value for r in CaseRole},
        conditions=HoareCondition(preconditions=["valid"], postconditions=["done"]),
    )
    defaults.update(overrides)
    return OPCContract(**defaults)


def _make_speq(*contracts: OPCContract) -> Speq:
    s = Speq(name="test_system", version="1.0.0")
    for c in contracts:
        s = s.add(c)
    return s


class TestValidationResult:
    def test_passed_when_no_errors(self):
        r = ValidationResult(errors=[], warnings=[])
        assert r.passed is True
        assert r.ready_for_certification is True

    def test_failed_when_errors(self):
        r = ValidationResult(errors=["bad"], warnings=[])
        assert r.passed is False
        assert r.ready_for_certification is False

    def test_passed_with_warnings(self):
        r = ValidationResult(errors=[], warnings=["heads up"])
        assert r.passed is True


class TestValidate:
    def test_valid_speq_passes(self):
        speq = _make_speq(_make_contract("a"), _make_contract("b"))
        result = validate(speq)
        assert result.passed

    def test_empty_speq_warns(self):
        speq = Speq(name="empty", version="1.0.0")
        result = validate(speq)
        assert result.passed
        assert len(result.warnings) > 0

    def test_missing_version_warns(self):
        speq = _make_speq(_make_contract("a"))
        speq = speq.model_copy(update={"version": ""})
        result = validate(speq)
        assert len(result.warnings) > 0

    def test_duplicate_targets_warns(self):
        c1 = _make_contract("a", target="mod.same")
        c2 = _make_contract("b", target="mod.same")
        speq = _make_speq(c1, c2)
        result = validate(speq)
        assert len(result.warnings) > 0

    def test_empty_role_value_errors(self):
        roles = {r: r.value for r in CaseRole}
        roles[CaseRole.AGENT] = ""
        c = OPCContract(
            name="bad",
            target="mod.bad",
            roles=roles,
            conditions=HoareCondition(preconditions=["valid"]),
        )
        speq = _make_speq(c)
        result = validate(speq)
        assert not result.passed

    def test_empty_target_errors(self):
        roles = {r: r.value for r in CaseRole}
        # model_construct bypasses pydantic validators so we can set target=""
        c = OPCContract.model_construct(
            name="no_target",
            target="",
            roles=roles,
            conditions=HoareCondition(preconditions=["valid"], postconditions=["done"]),
            guarantee_target=None,
            version="1",
            tags=[],
        )
        speq = Speq.model_construct(name="test_system", version="1.0.0", contracts=[c])
        result = validate(speq)
        assert not result.passed
        assert any("target is empty" in e for e in result.errors)

    def test_no_conditions_errors(self):
        roles = {r: r.value for r in CaseRole}
        # model_construct bypasses pydantic validators so we can have empty conditions
        c = OPCContract.model_construct(
            name="no_cond",
            target="mod.no_cond",
            roles=roles,
            conditions=HoareCondition(preconditions=[], postconditions=[]),
            guarantee_target=None,
            version="1",
            tags=[],
        )
        speq = Speq.model_construct(name="test_system", version="1.0.0", contracts=[c])
        result = validate(speq)
        assert not result.passed
        assert any("no preconditions or postconditions" in e for e in result.errors)
